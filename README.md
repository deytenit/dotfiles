# ᓭ⍑ᒷꖎꖎ ᒲᔑ⊣╎ᓵ <sup>[1](#footnote-1)</sup>

![Preview](./assets/preview.png)

A self-contained, cross-platform dotfiles management system with declarative YAML configuration and automated deployment.

## Overview

This repository contains my personal configuration files (dotfiles) for macOS and Linux systems. The system is built around a custom "strap" framework that makes it easy to deploy, manage, and synchronize configurations across different machines and platforms.

### What's Inside

Configurations for:

- **Terminal**: Fish shell, Ghostty
- **Editor**: Neovim
- **macOS**: Yabai (tiling WM), Skhd (hotkey daemon), Hammerspoon
- **Linux**: Hyprland, Waybar, Rofi, Dunst, Darkman
- **Multiplexer**: Zellij
- **Agent Harness**: Shared skills, instructions, and Codex agents
- **Git**: Custom aliases and semantic commit tool

### Key Features

- **Self-Contained Bootstrap**: Python 3.10+ with vendored interactive UI dependencies
- **Reviewed Setup**: Interactive selection and a final deployment review before changes are applied
- **Platform-Specific Configs**: Generic configuration combined with macOS or Linux settings
- **Declarative YAML Format**: Simple, readable configuration files
- **Automatic Symlink Management**: No manual linking required
- **Safe Copy Semantics**: Conflicts are preserved unless a strap explicitly authorizes replacement
- **Git Integration**: Built-in sync command with auto-commit and push
- **Cron Job Management**: Per-strap ownership with validation and rollback
- **Native Notifications**: Desktop notifications on macOS and Linux

## Quick Start

Clone the repository and run the bootstrap script:

```bash
git clone <your-repo-url> ~/.dotfiles
cd ~/.dotfiles
python3 bootstrap.py
```

Interactive setup lets you choose individual configurations or set up everything, then presents a final review before applying changes. Nothing is selected by default in Choose mode.

For explicit unattended deployment, use `--all`:

```bash
python3 bootstrap.py --all
```

The bootstrap process will:

1. Discover and validate all strap configuration files
2. Combine generic settings with the current Linux or macOS settings
3. Plan symlinks, copies, and cron changes without modifying the system
4. Show the complete deployment review
5. Apply the confirmed plan and abort if reviewed filesystem state changed
6. Set up the `deytefiles` command in your PATH

After bootstrap, you can use the `deytefiles` command from anywhere:

```bash
deytefiles sync              # Sync changes with git
deytefiles bootstrap         # Run the interactive bootstrap again
deytefiles bootstrap --all   # Set up every configuration without prompts
```

## Strap Configuration System

The heart of this dotfiles system is the "strap" framework. Each component has a YAML configuration file that defines how it should be deployed.

### File Naming

Accepted configuration filenames are:

- `strap.yaml` - The primary configuration in a directory
- `{id}.strap.yaml` - Additional independently selectable configurations in the same directory

Legacy executable `.strap` files and platform-suffixed filenames are rejected. Platform-specific actions live inside each strap's `platforms` mapping; `generic` actions combine with the current `linux` or `darwin` actions.

### YAML Format

Basic structure of a strap configuration file:

```yaml
name: component-name
category: System
description: Description shown during setup
platforms:
  generic:
    link:
      - file.conf
      - [source.conf, ~/.config/target.conf]
    copy:
      - [file.txt, ~/target.txt]
    cron:
      - ["0 * * * *", "~/script.sh"]
```

### Entry Formats

The `link` and `copy` sections support multiple formats for flexibility:

#### 1. Simple String (Automatic Target)

```yaml
platforms:
  generic:
    link:
      - config.fish
      - aliases.fish
```

The target path is automatically inferred from the directory structure.
Example: `config.fish` in `.config/fish/` → `~/.config/fish/config.fish`

#### 2. Explicit Target

```yaml
platforms:
  generic:
    link:
      - [source.conf, ~/.config/app/target.conf]
    copy:
      - [script.sh, ~/.local/bin/script.sh]
```

Specify both source and target paths explicitly.

#### 3. Current Directory

```yaml
platforms:
  generic:
    link:
      - [., ~/.config/nvim]
```

Link the entire directory containing the strap file.

### Examples

**Simple configuration** (`.config/fish/strap.yaml`):

```yaml
name: Fish
category: Terminal
description: Fish shell configuration
platforms:
  generic:
    link:
      - config.fish
      - aliases.fish
      - functions.fish
```

**With platform-specific targets** (`.config/darkman/strap.yaml`):

```yaml
name: Darkman
category: Desktop
description: Automatic light and dark themes
platforms:
  linux:
    link:
      - [config.yaml, ~/.config/darkman/config.yaml]
      - [dark-mode.d, ~/.local/share/dark-mode.d]
      - [light-mode.d, ~/.local/share/light-mode.d]
```

**Directory linking** (`.config/nvim/strap.yaml`):

```yaml
name: Neovim
category: Editor
description: Neovim editor configuration
platforms:
  generic:
    link:
      - [., ~/.config/nvim]
```

**With copy and cron** (`.config/app/strap.yaml`):

```yaml
name: App
category: System
description: Example application configuration
platforms:
  generic:
    link:
      - config.conf
    copy:
      - [.theme.conf, ~/.config/app/.theme.conf]
    cron:
      - ["0 * * * *", "~/script.sh"]
```

### Deployment Harness Example

The Agent Harness is split into independently selectable straps. For a Codex setup, choose **Shared skills**, **Shared instructions**, and **Codex agents** during interactive bootstrap.

Forced copies explicitly authorize replacement of managed files while preserving unrelated children in an existing destination directory:

```yaml
name: Shared skills
category: Agent Harness
description: Portable agent workflows
platforms:
  generic:
    copy:
      - source: skills
        target: ~/.agents/skills
        force: true
```

| Strap | Destinations |
| --- | --- |
| OpenCode | `~/.config/opencode/opencode.jsonc` |
| Shared skills | `~/.config/opencode/skills`, `~/.agents/skills`, `~/.claude/skills` |
| Shared instructions | `~/.config/opencode/AGENTS.md`, `~/.codex/AGENTS.md`, `~/.claude/CLAUDE.md`, `~/.gemini/GEMINI.md` |
| Codex agents | `~/.codex/agents` |

## deytefiles CLI Reference

The `deytefiles` command is the main interface for managing your dotfiles.

### Commands

#### bootstrap

Run the interactive bootstrap process:

```bash
deytefiles bootstrap        # Choose configurations and review the plan
deytefiles bootstrap --all  # Set up every configuration without prompts
deytefiles bootstrap -q     # Suppress completion notifications
```

Without `--all`, bootstrap requires an interactive terminal. The `-q` option suppresses notifications only; it does not make setup non-interactive.

#### sync

Synchronize local changes with the remote git repository:

```bash
deytefiles sync                      # Auto-commit with timestamp
deytefiles sync -m "Custom message"  # Custom commit message
deytefiles sync -f                   # Force push (--force-with-lease)
deytefiles sync -q                   # Quiet mode (no notifications)
```

This command:

1. Stages all changes (`git add -A`)
2. Creates a commit (with timestamp or custom message)
3. Pulls with rebase from origin
4. Pushes changes to remote
5. Handles conflicts gracefully
6. Sends a completion notification

### Options

- `-q, --quiet` - Suppress desktop notifications
- `-m, --message MESSAGE` - Custom sync commit message
- `-f, --force` - Use `--force-with-lease` when syncing
- `--all` - Set up every configuration without interactive prompts

## Repository Structure

```text
.dotfiles/
├── bootstrap.py              # Interactive bootstrap entry point
├── strap.yaml                # Root configuration
├── .codex/
│   ├── agents/               # Codex role definitions
│   └── strap.yaml            # Codex agents deployment
├── .config/
│   ├── fish/
│   │   ├── strap.yaml        # Fish shell config
│   │   ├── config.fish
│   │   ├── aliases.fish
│   │   └── functions.fish
│   ├── opencode/
│   │   ├── strap.yaml
│   │   ├── skills.strap.yaml
│   │   └── instructions.strap.yaml
│   └── nvim/
│       └── strap.yaml        # Neovim config
├── .local/
│   ├── bin/
│   │   ├── strap.yaml
│   │   └── deytefiles        # Dotfiles CLI
│   └── share/dotfiles/
│       ├── cli/              # CLI implementation
│       ├── strap/            # Bootstrap discovery, planning, UI, and execution
│       └── vendor/           # Vendored bootstrap dependencies
└── README.md
```

## Technical Details

### Vendored Bootstrap Dependencies

The interactive bootstrap uses vendored wheels for Questionary, prompt-toolkit, and wcwidth, so no package installation is needed. Checksums, licenses, upstream projects, and embedded notices are listed in `.local/share/dotfiles/vendor/THIRD_PARTY_LICENSES.md`.

### Reviewed Deployment

Bootstrap discovers and validates every strap before planning any changes. The final review shows links, copies, replacements, and cron updates together. Execution verifies that reviewed filesystem state is still current and aborts safely when it is stale.

Ordinary copies create missing targets, report matching targets as current, and preserve conflicting targets. A `force: true` copy authorizes replacement. Forced directory copies overlay managed children when the destination is a real directory and preserve unrelated children; otherwise the destination root is atomically replaced with a real directory copy.

### Cron Job Management

Cron entries are owned by individually marked strap sections:

- Selecting one strap updates only that strap's section
- Complete mode and `--all` reconcile every managed section
- Unmanaged crontab content is preserved
- Failed installation restores the original crontab

### Notification System

Desktop notifications use native OS facilities:

- **macOS**: AppleScript via `osascript`
- **Linux**: `notify-send` (works with dunst, mako, notification-daemon, etc.)

Notifications can be disabled with the `-q/--quiet` flag.

### Context-Aware Execution

The `deytefiles` command automatically determines the repository location based on its installation path, allowing it to work from any directory on your system. This is achieved through:

1. The `deytefiles` script calculates the repo root from its own location
2. All git operations use the repo path explicitly
3. Commands work regardless of your current working directory

## Footnotes

- <a name="footnote-1">[1]</a>: eng. Shell Magic _(Standard Galactic Alphabet)_
