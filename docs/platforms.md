# Supported Platforms

← [Back to README](../README.md)

Gentle AI supports **macOS on Apple Silicon and Intel**. Homebrew is the primary package manager. Releases publish only `darwin/arm64` and `darwin/amd64` archives; the installer and CLI reject Linux and Windows.

## OpenCode Managed Launcher

When OpenCode background subagents are enabled through `gentle-ai install` or `gentle-ai sync`, Gentle AI manages `~/.gentle-ai/bin/opencode`. It sets `OPENCODE_EXPERIMENTAL_BACKGROUND_SUBAGENTS=true` only when the variable is unset, so an explicit `false` selects foreground execution. Restart OpenCode after enabling the launcher, and restart the shell if its directory has not entered `PATH`.

Sessions started outside the managed launcher use foreground fallback. Deactivation removes managed launcher files but does not rewrite shell profiles.
