#!/bin/bash

OUTDATED=$(pacman -Qu | wc -l)

if [[ "$OUTDATED" -ne 0 ]]; then
  echo " <b>$OUTDATED</b> <sup>󰓧</sup>"
else
  echo ""
fi
