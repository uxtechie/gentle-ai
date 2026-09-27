#!/usr/bin/env python3
"""Run every Go package test, sharding the large CLI suite without omissions."""

import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from tempfile import TemporaryDirectory
from threading import Lock


CLI_SHARDS = (
    ("A-M", r"^Test[A-M]"),
    ("N-Q,S-Z", r"^Test[N-QS-Z]"),
    ("R", r"^TestR"),
)


def check_cli_coverage(listing):
    names = [line.strip() for line in listing.splitlines()
             if line.startswith(("Test", "Example", "Fuzz"))]
    if not names:
        raise ValueError("CLI test listing is empty")
    unmatched = [name for name in names
                 if sum(bool(re.match(pattern, name)) for _, pattern in CLI_SHARDS) != 1]
    if unmatched:
        raise ValueError("CLI tests not covered exactly once: " + ", ".join(unmatched))
    return len(names)


def test_environment(config_dir):
    env = os.environ.copy()
    env["XDG_CONFIG_HOME"] = config_dir
    for key in ("OPENCODE_CONFIG_DIR", "OPENCODE_CONFIG", "PI_CODING_AGENT_DIR"):
        env.pop(key, None)
    return env


def run_test_group(name, command, output_lock):
    with output_lock:
        print(f"Go test group {name}: starting", file=sys.stderr, flush=True)
    start = time.monotonic()
    with TemporaryDirectory(prefix="gentle-ai-go-test-config-") as config_dir:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   text=True, errors="replace", env=test_environment(config_dir))
        for line in process.stdout:
            with output_lock:
                sys.stdout.write(line)
                sys.stdout.flush()
        status = process.wait()
    with output_lock:
        print(f"Go test group {name}: {'PASS' if status == 0 else 'FAIL'} "
              f"({time.monotonic() - start:.1f}s)", file=sys.stderr,
              flush=True)
    return status


def main():
    packages = subprocess.check_output(["go", "list", "./..."], text=True).splitlines()
    cli = subprocess.check_output(["go", "list", "./internal/cli"], text=True).strip()
    others = [package for package in packages if package != cli]
    if cli not in packages or not others:
        raise ValueError("cannot partition the Go package list")
    listing = subprocess.check_output(["go", "test", "-list", ".", cli], text=True)
    count = check_cli_coverage(listing)
    print(f"Go test coverage: {len(others)} other packages, {count} CLI tests in "
          f"{len(CLI_SHARDS)} shards", file=sys.stderr, flush=True)

    groups = [("other packages", ["go", "test", "-json", "-p=2", *others])]
    groups.extend((name, ["go", "test", "-json", "-run", pattern, cli])
                  for name, pattern in CLI_SHARDS)
    output_lock = Lock()
    with ThreadPoolExecutor(max_workers=len(groups)) as pool:
        results = list(pool.map(lambda group: run_test_group(*group, output_lock), groups))
    return 0 if all(status == 0 for status in results) else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, subprocess.CalledProcessError) as exc:
        print(f"Go test partition refused: {exc}", file=sys.stderr)
        sys.exit(1)
