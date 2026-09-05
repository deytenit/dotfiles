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

mkdir -p "$HOME/.cache"
echo "$MODE" > "$HOME/.cache/hypr_wallpaper_mode"

is_on_ac() {
    local has_battery=0
    for b in /sys/class/power_supply/*; do
        if [[ -f "$b/type" && "$(< "$b/type")" == "Battery" ]]; then
            has_battery=1
            break
        fi
    done

    # If no battery in system (desktop PC), treat as always on AC
    if [[ $has_battery -eq 0 ]]; then
        return 0
    fi

    # Check for Mains power supplies online
    for p in /sys/class/power_supply/*; do
        if [[ -f "$p/type" && "$(< "$p/type")" == "Mains" ]]; then
            if [[ -f "$p/online" && "$(< "$p/online")" -eq 1 ]]; then
                return 0
            fi
        fi
    done

    # Fallback to upower if available
    if command -v upower >/dev/null 2>&1; then
        if upower -d 2>/dev/null | grep -q "on-battery:\s*no"; then
            return 0
        fi
    fi

    return 1
}

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
# If running on battery, do not start linux-wallpaperengine to conserve power.
if ! is_on_ac; then
    echo "Running on battery power. Keeping static wallpaper and disabling video wallpaper."
    pkill -f linux-wallpaperengine || true
    exit 0
fi

CONFIG_FILE="$HOME/.config/hypr/wallpapers/${MODE}_scenes.txt"

# If linux-wallpaperengine isn't installed or config is missing/empty, we gracefully stop here
# The static fallback will remain visible.
if ! command -v linux-wallpaperengine &> /dev/null || [[ ! -s "$CONFIG_FILE" ]]; then
    pkill -f linux-wallpaperengine # clean up any running engines just in case
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
