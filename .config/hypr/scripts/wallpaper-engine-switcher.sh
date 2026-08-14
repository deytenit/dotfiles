#!/usr/bin/env bash
exec > /tmp/wallpaper-switcher.log 2>&1
set -x

MODE=$1
if [[ -z "$XDG_SESSION_TYPE" ]]; then
    export XDG_SESSION_TYPE=wayland
fi
if [[ "$MODE" != "dark" && "$MODE" != "light" ]]; then
    echo "Usage: $0 <dark|light>"
    exit 1
fi

MONITORS=($(hyprctl -i 0 monitors | grep Monitor | awk '{print $2}'))

# --- 1. Static Wallpaper Fallback / Base Layer ---
# Capitalize mode for folder name (dark -> Dark, light -> Light)
STATIC_DIR="$HOME/Pictures/Wallpapers/${MODE^}"
if [[ -d "$STATIC_DIR" ]]; then
    STATIC_WP=$(find "$STATIC_DIR" -type f | shuf -n 1)
    if [[ -n "$STATIC_WP" ]]; then
        hyprctl -i 0 -q hyprpaper unload all
        hyprctl -i 0 -q hyprpaper preload "$STATIC_WP"
        sleep 0.5
        for m in "${MONITORS[@]}"; do
            hyprctl -i 0 -q hyprpaper wallpaper "$m,$STATIC_WP"
        done
    fi
fi

# --- 2. Video Wallpaper ---
CONFIG_FILE="$HOME/.config/hypr/wallpapers/${MODE}_scenes.txt"

# If linux-wallpaperengine isn't installed or config is missing/empty, we gracefully stop here
# The static fallback will remain visible.
if ! command -v linux-wallpaperengine &> /dev/null || [[ ! -s "$CONFIG_FILE" ]]; then
    pkill -x linux-wallpaperengine # clean up any running engines just in case
    exit 0
fi

# Pick a random workshop ID
WORKSHOP_ID=$(shuf -n 1 "$CONFIG_FILE")

# Kill existing wallpaper engines before starting new ones
pkill -f linux-wallpaperengine

# Launch new video wallpapers over the static base
for m in "${MONITORS[@]}"; do
    linux-wallpaperengine --screen-root "$m" --bg "$WORKSHOP_ID" --scaling fill --layer background --fps 60 --no-fullscreen-pause &
done
