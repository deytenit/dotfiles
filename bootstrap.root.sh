#!/usr/bin/env bash

#
# Root-level dotfile linker for global files
#
set -euo pipefail
IFS=$'\n\t'

#----------------------------------------
# Link .gitconfig
#----------------------------------------
src="$PWD/.gitconfig"
dest="$HOME/.gitconfig"

echo "Linking .gitconfig → $dest"
ln -sf "$src" "$dest"
