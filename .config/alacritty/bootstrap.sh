#!/usr/bin/env bash
set -euo pipefail

# Ensure destination directory exists
dest="$HOME/.config/alacritty"
mkdir -p "$dest"

# Link theme files
declare -A files=(
  [alacritty.toml]="alacritty.toml"
  [dark.toml]="dark.toml"
  [light.toml]="light.toml"
)

for src in "${!files[@]}"; do
  tgt="$dest/${files[$src]}"
  ln -sf "$PWD/$src" "$tgt"
  echo "Linked $src -> $tgt"
done

cp "$PWD/.theme.toml" "$dest/.theme.toml"
echo "Copied .theme.toml -> $dest/.theme.toml"
