#!/usr/bin/env bash
set -euo pipefail

dest="$HOME/.config/nvim"
rm -rf "$dest"
mkdir -p "$(dirname "$dest")"
ln -s "$PWD" "$dest"
echo "Linked .config/nvim -> $dest"
