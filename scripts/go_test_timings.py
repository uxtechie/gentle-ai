#!/usr/bin/env python3
"""Summarize Go's per-test JSON events without losing the complete raw log."""

import json
import sys
from datetime import datetime


def summarize(lines):
    started = {}
    completed = []
    failed = []
    last_time = None
    for line in lines:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue  # Compiler errors are plain text, not test events.
        action = event.get("Action")
        package = event.get("Package", "")
        test = event.get("Test")
        event_time = datetime.fromisoformat(event["Time"]) if event.get("Time") else None
        if event_time and (last_time is None or event_time > last_time):
            last_time = event_time
        if action == "run" and test:
            started[(package, test)] = event_time
        elif action in ("pass", "fail", "skip") and test:
            started.pop((package, test), None)
            if action != "skip":
                completed.append((event.get("Elapsed", 0), package, test))
            if action == "fail":
                failed.append((package, test))
        elif action == "fail" and not test:
            failed.append((package, None))
    return completed, failed, started, last_time


def format_summary(lines):
    completed, failed, started, last_time = summarize(lines)
    output = ["Slowest completed Go tests (elapsed includes subtests):"]
    for elapsed, package, test in sorted(completed, reverse=True)[:10]:
        output.append(f"  {elapsed:.2f}s {package} {test}")
    if failed:
        output.append("Failed tests/packages: " + ", ".join(
            f"{package} {test}" if test else package for package, test in failed[:10]
        ))
    if started:
        output.append("Still running when output ended (not necessarily the cause):")
        for (package, test), since in list(started.items())[:10]:
            elapsed = (last_time - since).total_seconds() if last_time and since else 0
            output.append(f"  {elapsed:.1f}s {package} {test}")
    return "\n".join(output)


if __name__ == "__main__":
    with open(sys.argv[1], encoding="utf-8", errors="replace") as log:
        print(format_summary(log))
