#!/usr/bin/env bash
set -euo pipefail

dest="$HOME/.config/waybar"
rm -rf "$dest"
mkdir -p "$(dirname "$dest")"
ln -s "$PWD" "$dest"
echo "Linked .config/waybar -> $dest"
