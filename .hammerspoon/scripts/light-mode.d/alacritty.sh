#!/usr/bin/env bash

/opt/homebrew/bin/gsed -i '/# BEGIN_ALACRITTY_THEME/,/# END_ALACRITTY_THEME/c\
# BEGIN_ALACRITTY_THEME\
general.import = [ "~/.config/alacritty/light.toml" ]\
# END_ALACRITTY_THEME' ~/.config/alacritty/.theme.toml
