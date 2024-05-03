#!/bin/bash

UPDATE=$(pacman -Qu | wc -l)
FOREIGN=$((pacman -Qm) | wc -l)

if [[ "$UPDATE" -ne 0 ]]; then
    echo "<b>$FOREIGN</b> <sup>󰓧</sup>"
else
    echo "<b>$FOREIGN</b>"
fi
