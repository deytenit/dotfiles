#!/usr/bin/env bash

sed -i '/\/\*BEGIN_WAYBAR_THEME\*\//,/\/*END_WAYBAR_THEME\*\//c\/*BEGIN_WAYBAR_THEME*/\n@import url("./dark.css");\n/*END_WAYBAR_THEME*/' ~/.config/waybar/.theme.css
pkill -SIGUSR2 waybar
