# Quickstart

## Prerequisites

### macOS

- Homebrew installed and available in PATH.
- `git` available.
- If Homebrew requires trust, run `brew trust --formula gentleman-programming/tap/gentle-ai` once for Gentle AI™ only.
  - To install several tools from this tap, use `brew trust gentleman-programming/tap` instead. It trusts all current and future formulas, casks, and external commands published in the tap.

- Git 2.38+.
- Go 1.25.10+ (for building from source).
- Node.js 18+ and npm. Gentle AI checks these prerequisites and does not install agent runtimes for you.
- Pi installed and available as `pi` on `PATH` if you select the Pi agent.

## Version Policy

Receipt-Driven Development (RDD) began in `v1.47.0` on 2026-07-10, and `v2.2.0` made it the supported stable path. Those are historical milestones. The negotiated public review contract was published in `v2.1.6`.

The current stable release is [`v2.6.0`](https://github.com/Gentleman-Programming/gentle-ai/releases/tag/v2.6.0). `@latest` explicitly tracks this stable channel. No prerelease is ahead of stable. `@main` installs unreleased development changes.

### Install the stable channel

```bash
go install github.com/gentleman-programming/gentle-ai/v3/cmd/gentle-ai@latest
gentle-ai version
```

### Install unreleased development changes

Only use `main` when testing changes that are not part of a release yet:

```bash
go install github.com/gentleman-programming/gentle-ai/v3/cmd/gentle-ai@main
gentle-ai version
```

To update a beta installation later, preserve the beta channel:

```bash
GENTLE_AI_CHANNEL=beta gentle-ai upgrade
```

`gentle-ai upgrade` advances the `gentle-ai` binary from `main` and refreshes managed tools on macOS with Go on `PATH`.

If you re-run the installer, pass beta explicitly because it defaults to stable:

```bash
curl -fsSL https://raw.githubusercontent.com/Gentleman-Programming/gentle-ai/main/scripts/install.sh | bash -s -- --channel beta
```

> **Go module proxy cache**: `proxy.golang.org` can lag behind new commits on `main`. If manual `go install ...@main` is stale, use `GOPROXY=direct go install github.com/gentleman-programming/gentle-ai/v3/cmd/gentle-ai@main`.

The managed install scripts select the latest version for their chosen channel and do not accept arbitrary release pins. Use `go install` with an exact tag when you need a reproducible prerelease or stable version.

## Run

```bash
go run ./cmd/gentle-ai install --dry-run
```

Use `--dry-run` first to validate selections and execution plan without applying changes. The dry-run output includes a `Platform decision` line showing the detected OS, distro, package manager, and support status.

## First real install

```bash
go run ./cmd/gentle-ai install
```

The installer requires macOS and resolves system packages through Homebrew.

After completion, verify that agent configs and selected components were installed to their expected paths.

The agents you select during install become the default scope for future `gentle-ai sync` runs. Gentle AI records that selection in `~/.gentle-ai/state.json` and does not automatically sync every agent config directory that exists on your machine. To check what will be updated after an upgrade, run:

```bash
gentle-ai sync --dry-run
```

To update a different set explicitly, pass every target agent:

```bash
gentle-ai sync --agent claude-code --agent opencode
```

## Verification outcome

When checks pass, installer reports:

`You're ready. Run 'claude' or 'opencode' and start building.`

If something looks wrong after install, run `gentle-ai doctor` for a read-only health check. It verifies tool binaries, `state.json` validity, Engram™ MCP reachability, and disk space — each check reports pass/warn/fail with a remedy hint.

For a Pi-only install, the plan shows the Pi package stack instead of Gentle AI components. It installs `gentle-pi`, `gentle-engram`, and `pi-mcp-adapter`, runs `pi-engram init` through the pinned `gentle-engram` package, then installs `pi-web-access` and `pi-btw`.

## Start working with ODD

Open your agent in the project and describe an outcome, for example: "Add CSV export using the existing report filters." [Organic Driven Development (ODD)](usage.md#organic-driven-development-odd) is the development workflow: explore, implement authorized work, and check it. Substantial work keeps one recoverable feature document; small/read-only work avoids durable artifacts.

## Hardening recommendations for users

Gentle AI pins versions and disables postinstall scripts on every npm install it generates. When you install the `permissions` component, a sensitive-paths deny list is applied to Claude Code and OpenCode blocking access to `~/.ssh/*`, `**/*.pem`, `**/*.key`, `**/.env*`, `~/.aws/credentials`, and other credential paths. See [Components](../docs/components.md) for the full list.

For broader protection across npm packages you install yourself, set these once on your machine:

- `npm config set ignore-scripts true` — blocks postinstall scripts globally; the primary supply-chain attack vector.
- `npm config set min-release-age 3` — skip packages published in the last 3 days; catches malicious typosquats before you install them.
- `npm config set allow-git none` — block git: dependencies, which can be moving targets.

Optional wrapper tools for extra defense:

- [`npq`](https://github.com/lirantal/npq) — audits a package against several heuristics before it installs.
- [`sfw`](https://socket.dev/) (Socket Firewall) — runtime guard that intercepts suspicious behavior at install/run time.

## Unsupported platforms

On Linux or Windows, the installer exits immediately with an error:

- `Unsupported OS: <os>. Only macOS is supported.`
