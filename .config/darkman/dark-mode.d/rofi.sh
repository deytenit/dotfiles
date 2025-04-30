#!/usr/bin/env bash

sed -i '/\/\*BEGIN_ROFI_THEME\*\//,/\/*END_ROFI_THEME\*\//c\/*BEGIN_ROFI_THEME*/\n@import "./dark.rasi"\n/*END_ROFI_THEME*/' ~/.config/rofi/config/.theme.rasi
