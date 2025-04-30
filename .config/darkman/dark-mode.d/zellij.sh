#!/usr/bin/env bash

sed -i '/\/\/ BEGIN_ZELLIJ_THEME/,/\/\/ END_ZELLIJ_THEME/c\
\/\/ BEGIN_ZELLIJ_THEME\
theme "rainby-dark"\
\/\/ END_ZELLIJ_THEME' ~/.config/zellij/config.kdl
