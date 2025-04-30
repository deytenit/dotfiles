#!/usr/bin/env bash

INTERVAL=$1
DIR=$2

if [[ -z "$INTERVAL" || -z "$DIR" ]]; then
  echo "Usage: $0 <INTERVAL> <DIR>"
  exit 1
fi

LOCK="$HOME/.lock/hyprpaper-random.lock"

# Terminate any existing instance of this script
if pids=$(lsof -t "$LOCK"); then
  kill -15 $pids
fi

(
flock -n 100 || exit
MONITOR=($(hyprctl -i 0 monitors | grep Monitor | awk '{print $2}'))
wallpapers=()
used_wallpapers=()

# Function to populate the wallpapers array if empty
load_wallpapers() {
  wallpapers=($(find "${DIR}" -type f | shuf))
}

# Initial load of wallpapers
load_wallpapers

while true; do
  # Refill wallpapers list if all have been used
  if [ ${#wallpapers[@]} -eq 0 ]; then
    load_wallpapers
    used_wallpapers=()
  fi

  # Pick and remove the first wallpaper from the list
  wallpaper="${wallpapers[0]}"
  wallpapers=("${wallpapers[@]:1}")
  used_wallpapers+=("$wallpaper")

  # Set the wallpaper on all monitors
  hyprctl -i 0 -q hyprpaper unload all
  hyprctl -i 0 -q hyprpaper preload "$wallpaper"
  for m in "${MONITOR[@]}"; do
    hyprctl -i 0 -q hyprpaper wallpaper "$m,$wallpaper"
  done

  sleep "$INTERVAL"
done
) 100> "$LOCK"

