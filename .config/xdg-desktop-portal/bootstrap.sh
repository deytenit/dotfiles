#!/usr/bin/env bash
set -euo pipefail

dest_dir="$HOME/.config/xdg-desktop-portal"
mkdir -p "$dest_dir"
ln -sf "$PWD/portals.conf" "$dest_dir/portals.conf"
echo "Linked portals.conf -> $dest_dir/portals.conf"
