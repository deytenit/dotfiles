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
- **Git**: Custom aliases and semantic commit tool

### Key Features

- **No External Dependencies**: Includes vendored YAML parser, works out-of-the-box with Python 3
- **Platform-Specific Configs**: Separate configurations for macOS and Linux
- **Declarative YAML Format**: Simple, readable configuration files
- **Automatic Symlink Management**: No manual linking required
- **Git Integration**: Built-in sync command with auto-commit and push
- **Cron Job Management**: Automated scheduling with validation and rollback
- **Native Notifications**: Desktop notifications on macOS and Linux

## Quick Start

Clone the repository and run the bootstrap script:

```bash
git clone <your-repo-url> ~/.dotfiles
cd ~/.dotfiles
python3 bootstrap.py
```

The bootstrap process will:

1. Process all strap configuration files
2. Create symlinks to your home directory
3. Copy files that need customization
4. Install cron jobs (if configured)
5. Set up the `deytefiles` command in your PATH

After bootstrap, you can use the `deytefiles` command from anywhere:

```bash
deytefiles sync              # Sync changes with git
deytefiles bootstrap         # Re-run bootstrap process
```

## Strap Configuration System

The heart of this dotfiles system is the "strap" framework. Each component has a YAML configuration file that defines how it should be deployed.

### File Naming

Configuration files use platform-specific naming:

- `strap.yaml` - Cross-platform configuration (deployed everywhere)
- `strap@darwin.yaml` - macOS-specific configuration
- `strap@linux.yaml` - Linux-specific configuration

The bootstrap process automatically selects the appropriate files for your current platform.

### YAML Format

Basic structure of a strap configuration file:

```yaml
name: component-name
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
link:
  - config.fish
  - aliases.fish
```

The target path is automatically inferred from the directory structure.
Example: `config.fish` in `.config/fish/` → `~/.config/fish/config.fish`

#### 2. Explicit Target

```yaml
link:
  - [source.conf, ~/.config/app/target.conf]
  - [script.sh, ~/.local/bin/script.sh]
```

Specify both source and target paths explicitly.

#### 3. Current Directory

```yaml
link:
  - [., ~/.config/nvim]
```

Link the entire directory containing the strap file.

### Examples

**Simple configuration** (`.config/fish/strap.yaml`):

```yaml
name: fish
link:
  - config.fish
  - aliases.fish
  - functions.fish
```

**With explicit targets** (`.config/darkman/strap@linux.yaml`):

```yaml
name: darkman
link:
  - [config.yaml, ~/.config/darkman/config.yaml]
  - [dark-mode.d, ~/.local/share/dark-mode.d]
  - [light-mode.d, ~/.local/share/light-mode.d]
```

**Directory linking** (`.config/nvim/strap.yaml`):

```yaml
name: nvim
link:
  - [., ~/.config/nvim]
```

**With copy and cron** (`.config/app/strap.yaml`):

```yaml
name: app
link:
  - config.conf
copy:
  - [.theme.conf, ~/.config/app/.theme.conf]
cron:
  - ["0 * * * *", "~/.local/bin/hourly-sync.sh"]
```

## deytefiles CLI Reference

The `deytefiles` command is the main interface for managing your dotfiles.

### Commands

#### bootstrap

Run the bootstrap process to deploy all configurations:

```bash
deytefiles bootstrap        # Full bootstrap with notifications
deytefiles bootstrap -q     # Quiet mode (no notifications)
```

This command:

1. Locates the dotfiles repository
2. Processes all strap files for your platform
3. Creates symlinks and copies files
4. Applies cron jobs
5. Sends a completion notification

#### sync

Synchronize local changes with the remote git repository:

```bash
deytefiles sync                    # Auto-commit with timestamp
deytefiles sync -m "Custom message"  # Custom commit message
deytefiles sync -f                 # Force push (--force-with-lease)
deytefiles sync -q                 # Quiet mode (no notifications)
```

This command:

1. Stages all changes (`git add -A`)
2. Creates a commit (with timestamp or custom message)
3. Pulls with rebase from origin
4. Pushes changes to remote
5. Handles conflicts gracefully
6. Sends a notification on completion or failure

### Options

- `-q, --quiet` - Suppress desktop notifications
- `-m, --message MESSAGE` - Custom commit message for sync
- `-f, --force` - Use `--force-with-lease` when pushing

## Repository Structure

```text
.dotfiles/
├── bootstrap.py              # Main bootstrap script
├── strap.yaml                # Root configuration
├── .config/                  # Application configurations
│   ├── fish/
│   │   ├── strap.yaml        # Fish shell config
│   │   ├── config.fish
│   │   ├── aliases.fish
│   │   └── functions.fish
│   ├── nvim/
│   │   └── strap.yaml        # Neovim config
│   ├── yabai/
│   │   └── strap@darwin.yaml # macOS-only
│   └── hypr/
│       └── strap@linux.yaml  # Linux-only
├── .hammerspoon/
│   └── strap@darwin.yaml     # Hammerspoon (macOS)
├── .local/
│   ├── bin/
│   │   ├── strap.yaml
│   │   ├── deytefiles        # CLI command
│   │   ├── copy              # Utility scripts
│   │   └── git-semantic
│   └── share/
│       └── dotfiles/
│           ├── utils.py      # Core utilities
│           ├── cli/          # CLI implementation
│           └── vendor/       # Vendored dependencies
│               └── yaml_parser.py
└── README.md
```

## Technical Details

### Vendored YAML Parser

This dotfiles system includes a custom, minimal YAML parser that requires no external dependencies. This means you can bootstrap on any system with Python 3 installed, without needing pip or internet access.

The parser supports all features needed for strap files:

- Key-value pairs (strings, numbers, booleans)
- Lists (block and flow style)
- Nested structures
- Comments

### Cron Job Management

The system can automatically manage cron jobs through the `cron` section in strap files. Features:

- **Validation**: All cron expressions are validated before applying
- **Isolated Section**: Jobs are placed in a dedicated section marked with comments
- **Automatic Rollback**: If cron installation fails, the original crontab is restored
- **Platform Support**: Works on macOS and Linux

Example cron section in crontab:

```cron
# BEGIN DEYTENIT DOTFILES STRAP CRON
0 * * * * ~/.local/bin/hourly-sync.sh
*/30 * * * * ~/.local/bin/backup.sh
# END DEYTENIT DOTFILES STRAP CRON
```

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
