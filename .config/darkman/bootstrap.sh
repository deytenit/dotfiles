#!/usr/bin/env bash
set -euo pipefail

# Config
cfg_src="$PWD/config.yaml"
cfg_dest="$HOME/.config/darkman/config.yaml"
mkdir -p "$(dirname "$cfg_dest")"
ln -sf "$cfg_src" "$cfg_dest"
echo "Linked config.yaml -> $cfg_dest"

# Modes
for mode in dark-mode.d light-mode.d; do
  src_dir="$PWD/$mode"
  dest_dir="$HOME/.local/share/$mode"
  rm -rf "$dest_dir"
  mkdir -p "$(dirname "$dest_dir")"
  ln -s "$src_dir" "$dest_dir"
  echo "Linked $mode -> $dest_dir"
done
