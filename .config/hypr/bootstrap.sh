#!/usr/bin/env bash
set -euo pipefail

# Link entire hypr directory
dest="$HOME/.config/hypr"
rm -rf "$dest"
mkdir -p "$(dirname "$dest")"
ln -s "$PWD" "$dest"
echo "Linked .config/hypr -> $dest"
