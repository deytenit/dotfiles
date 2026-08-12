# Shell Magic

Self-contained macOS and Linux dotfiles with a reviewed, declarative bootstrap flow. Python 3.10+ is required; the interactive terminal UI and its pure-Python dependencies are vendored in this repository.

## Deploy the agent harness

To set up the agent harness on a new machine, clone this repository and start the interactive bootstrap:

```bash
git clone <your-repo-url> ~/.dotfiles
cd ~/.dotfiles
python3 bootstrap.py
```

Choose configurations, select the **Agent Harness** entries you need, then confirm the final review. For a Codex setup, select **Shared skills**, **Shared instructions**, and **Codex agents**. This installs the shared skills and instructions and copies the Codex agent definitions to `~/.codex/agents`.

## Quick start

```bash
git clone <your-repo-url> ~/.dotfiles
cd ~/.dotfiles
python3 bootstrap.py
```

Interactive setup first asks whether to choose configurations or set up everything, then shows a final review. Nothing is selected by default in choose mode. For explicit unattended deployment use:

```bash
python3 bootstrap.py --all
deytefiles bootstrap --all
```

Without `--all`, bootstrap requires an interactive terminal. `deytefiles bootstrap -q` suppresses notifications only.

## Strap files

Accepted filenames are `strap.yaml` and `{id}.strap.yaml`; legacy executable `.strap` files and platform-suffixed names are rejected. Every strap has a name, category, and platform blocks. `generic` combines with the current `linux` or `darwin` block.

```yaml
name: Example
category: Desktop
platforms:
  generic:
    link:
      - config.ini
  linux:
    copy:
      - [theme.ini, ~/.config/example/theme.ini]
```

Links accept a source string or `[source, target]`. Concise targets mirror the repository path beneath the home directory. Ordinary copies create missing targets, report matching targets as current, and leave conflicting targets unchanged. Forced copies explicitly authorize replacement:

```yaml
name: Shared skills
category: Agent Harness
platforms:
  generic:
    copy:
      - source: skills
        target: ~/.agents/skills
        force: true
```

A forced directory copy overlays same-named managed children when its destination is a real directory, preserving unrelated children. If its destination root is missing, a file, or a symlink, bootstrap atomically replaces the root with a real full-directory copy. Links may replace reviewed conflicts. All filesystem changes are planned before execution and stale state aborts safely.

Cron entries are owned by individually marked strap sections. Selecting one strap updates only that section; Complete mode and `--all` reconcile all managed sections while preserving unmanaged crontab content.

## Agent harness

The harness parts are independently selectable.

| Strap | Destinations |
| --- | --- |
| OpenCode | `~/.config/opencode/opencode.jsonc` |
| Shared skills | `~/.config/opencode/skills`, `~/.agents/skills`, `~/.claude/skills` |
| Shared instructions | `~/.config/opencode/AGENTS.md`, `~/.codex/AGENTS.md`, `~/.claude/CLAUDE.md`, `~/.gemini/GEMINI.md` |
| Codex agents | `~/.codex/agents` |

## Vendored dependencies

Questionary 2.1.1, prompt-toolkit 3.0.52, and wcwidth 0.8.2 are embedded as wheels. Their checksums, licenses, upstream projects, and embedded notices are listed in `.local/share/dotfiles/vendor/THIRD_PARTY_LICENSES.md`.
