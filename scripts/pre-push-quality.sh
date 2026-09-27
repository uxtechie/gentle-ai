#!/usr/bin/env bash
# Run macOS CI checks before pushing. Logs stay off the hook's output on success.
set -euo pipefail
# The Go fixture suite asserts normal user-created file modes (0644/0755).
# An operator's restrictive shell umask must not turn fixture setup red.
umask 022

cd "$(git rev-parse --show-toplevel)"
if [ "$(uname -s)" != Darwin ]; then
  printf 'pre-push: only macOS is supported\n' >&2
  exit 1
fi

for tool in go node npm python3 jq; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    printf 'pre-push: %s is required; see CONTRIBUTING.md (Local pre-push checks)\n' "$tool" >&2
    exit 1
  fi
done
if [ -n "$(git status --porcelain --untracked-files=normal)" ]; then
  printf 'pre-push: commit or remove worktree changes before testing the push candidate\n' >&2
  exit 1
fi

work=$(mktemp -d "${TMPDIR:-/tmp}/gentle-ai-pre-push.XXXXXX")
cleanup() {
  local status=$?
  if [ "$status" -eq 0 ]; then
    rm -rf -- "$work"
  else
    printf 'pre-push: logs and benchmark results: %s\n' "$work" >&2
  fi
}
trap cleanup EXIT
count=0

check() {
  local name=$1 log
  shift
  count=$((count + 1))
  log="$work/$(printf '%02d' "$count").log"
  if "$@" >"$log" 2>&1; then
    printf '  PASS %s\n' "$name"
  else
    printf '  FAIL %s (last 20 lines; full log: %s)\n' "$name" "$log" >&2
    tail -n 20 "$log" >&2
    return 1
  fi
}

bench_module() {
  (cd bench && go build -o "$work/gentle-ai-bench" . && go vet ./... && go test ./...)
}

# Pin CI's required evidence: an unsupported journey must not look like a pass.
required_core=(
  j51-negotiated-status-correction-continuation
  j59-current-status-and-start-ignore-sibling-worktree-transaction
  j60-explicit-active-lineage-keeps-four-lens-correction-and-validator-flow
  j75-intended-untracked-selection-executes-printed-start
  j89-staged-validation-is-informational-and-unmanaged
  j104-repository-context-survives-fresh-process
  j110-untracked-terminal-burn-and-unmanaged-staged-validation
  j111-approved-transaction-burns-and-shipped-gates-are-unmanaged
  j113-correction-removes-candidate-only-path
  j114-last-reviewer-capture-closes-and-burns
  j116-codex-committed-correction-runs-returned-status-continuation
  j123-rejected-provider-validator-starts-fresh-high-risk-review
  j4435-selected-untracked-correction-continuation-is-selectorless
)
completed_once() {
  local result=$1 id=$2
  jq -e --arg id "$id" '[.journeys[] | select(.id == $id and .status == "completed")] | length == 1' "$result"
}
core_evidence() {
  local id
  for id in "${required_core[@]}"; do
    completed_once "$work/bench-portable.json" "$id" || return 1
  done
}
transition_evidence() {
  jq -e '([.journeys[] | select(.id | startswith("tr"))] | length) == 1' "$work/bench-transition.json" &&
    completed_once "$work/bench-transition.json" tr09-mode-flip-while-a-review-lineage-is-open
}

printf 'pre-push: running local quality checks (full logs kept only on failure)\n'
check 'Go format' go run ./internal/gofmtcheck
check 'Go vet' go vet ./...
check 'Go tests' go test ./...
check 'PR workflow script tests' node --test .github/scripts/parse-linked-issues.test.cjs .github/scripts/check-pr-size.test.cjs
check 'Installer module path' bash scripts/test-install-module-path.sh
check 'OpenCode V2 host tests' python3 -B -m unittest discover -s scripts -p test_opencode_v2_host_test.py
check 'OpenCode V2 released SDK contracts' bash scripts/test-opencode-v2-contracts.sh
check 'Bench build, vet and tests' bench_module
check 'Build product' go build -trimpath -o "$work/gentle-ai" ./cmd/gentle-ai
check 'Driven benchmark corpus' "$work/gentle-ai-bench" run --binary "$work/gentle-ai" --out "$work/bench-portable.json"
check 'Required benchmark journeys' core_evidence
check 'Provider capture journey' "$work/gentle-ai-bench" run --binary "$work/gentle-ai" --only j105-compiled-provider-capture-retries-same-binding --out "$work/bench-provider-capture.json"
check 'Provider capture evidence' completed_once "$work/bench-provider-capture.json" j105-compiled-provider-capture-retries-same-binding
check 'Transition axis' "$work/gentle-ai-bench" run --binary "$work/gentle-ai" --axis transition --out "$work/bench-transition.json"
check 'Transition evidence' transition_evidence
check 'Untagged model-picker axis' "$work/gentle-ai-bench" run --binary "$work/gentle-ai" --axis model-picker --only j97-opencode-custom-agent-model-picker-runtime --out "$work/bench-model-picker-untagged.json"
check 'Untagged model-picker evidence' jq -e '[.journeys[] | select(.id == "j97-opencode-custom-agent-model-picker-runtime" and .status == "unsupported")] | length == 1' "$work/bench-model-picker-untagged.json"
check 'Build tagged model-picker fixture' go build -tags bench_fixture -trimpath -o "$work/gentle-ai-bench-fixture" ./cmd/gentle-ai
check 'Tagged model-picker axis' "$work/gentle-ai-bench" run --binary "$work/gentle-ai-bench-fixture" --axis model-picker --only j97-opencode-custom-agent-model-picker-runtime --out "$work/bench-model-picker.json"
check 'Tagged model-picker evidence' completed_once "$work/bench-model-picker.json" j97-opencode-custom-agent-model-picker-runtime
check 'Dead-code ratchet' bash scripts/deadcode-ratchet.sh
check 'Darwin release-blocker manifest' bash scripts/darwin-release-blockers.sh verify
check 'Darwin release-blocker tests' bash scripts/darwin-release-blockers.sh run
check 'Cross-lane deterministic integration' bash scripts/cross-lane-battery.sh --binary "$work/gentle-ai"

printf 'pre-push: %d checks passed\n' "$count"
