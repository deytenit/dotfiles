#!/usr/bin/env bash
# waybar.sh
# Launches waybar, blueman-applet, and nm-applet.
# For waybar: attempts to launch until a waybar process for this user is visible, then exits.
# If waybar was already running, exits immediately. Once the script exits it DOES NOT
# monitor or resurrect waybar later.
# For applets: launches them in the background with appropriate retry logic.

set -euo pipefail

# --- Configurable vars ---
DELAY=0.5         # seconds to wait after each waybar launch attempt
MAX_RETRIES=0     # 0 = infinite retries for waybar; >0 = maximum number of attempts
BLUEMAN_MAX_RETRIES=10  # maximum attempts for blueman-applet
# -------------------------

# Check whether a process is running for the current user.
is_running() {
    local process_name="$1"
    if command -v pgrep >/dev/null 2>&1; then
        pgrep -u "$(id -u)" -x "$process_name" >/dev/null 2>&1
        return $?
    else
        ps -o pid= -u "$(id -u)" | xargs -r -n1 -I{} sh -c 'read -r pid; [ -n "$(ps -p "$pid" -o comm= 2>/dev/null | grep -x '"$process_name"' || true)" ]' >/dev/null 2>&1 \
            && return 0 || return 1
    fi
}

# Function to launch nm-applet
launch_nm_applet() {
    if ! command -v nm-applet >/dev/null 2>&1; then
        echo "WARNING: 'nm-applet' executable not found in PATH." >&2
        return 1
    fi
    
    if is_running "nm-applet"; then
        echo "nm-applet already running."
        return 0
    fi
    
    echo "Launching nm-applet..."
    setsid nm-applet >/dev/null 2>&1 </dev/null &
}

# Function to launch blueman-applet with retry logic
launch_blueman_applet() {
    if ! command -v blueman-applet >/dev/null 2>&1; then
        echo "WARNING: 'blueman-applet' executable not found in PATH." >&2
        return 1
    fi
    
    if is_running "blueman-applet"; then
        echo "blueman-applet already running."
        return 0
    fi
    
    echo "Launching blueman-applet..."
    
    # Initial attempt to start the blueman-applet
    blueman-applet >/dev/null 2>&1 &
    sleep 5
    
    # Do the first check and kill the first instance that fails to draw icon
    if is_running "blueman-applet"; then
        pkill -x "blueman-applet"
        sleep 2
    fi
    
    # Try again
    blueman-applet >/dev/null 2>&1 &
    sleep 2
    
    # Check if ok and if ok exit before the loop
    if is_running "blueman-applet"; then
        echo "blueman-applet started successfully."
        return 0
    fi
    
    # Init the counter to not loop indefinitely
    local counter=0
    # Loop to try and start the blueman-applet
    while [ $counter -lt "$BLUEMAN_MAX_RETRIES" ]; do
        # Try to start blueman-applet
        blueman-applet >/dev/null 2>&1 &
        # Sleep for 2 seconds before the next check...
        sleep 2
        # Check if success
        if is_running "blueman-applet"; then
            echo "blueman-applet started successfully on attempt $((counter + 1))."
            return 0
        else
            # Prompt if attempt failed (only if notify-send is available)
            if command -v notify-send >/dev/null 2>&1; then
                notify-send -u normal "Attempt $((counter + 1)) to start bluetooth tray applet failed."
            fi
        fi
        ((counter++))
    done
    
    # Final check and if all fails then prompt
    if ! is_running "blueman-applet"; then
        echo "ERROR: Failed to start blueman-applet after $BLUEMAN_MAX_RETRIES attempts." >&2
        if command -v notify-send >/dev/null 2>&1; then
            notify-send -u critical "Couldn't start bluetooth tray applet!"
        fi
        return 1
    fi
}

# Launch applets in the background (non-blocking)
launch_nm_applet &
launch_blueman_applet &

# --- Main waybar launch logic (unchanged) ---

# Ensure the binary exists before looping.
if ! command -v waybar >/dev/null 2>&1; then
    echo "ERROR: 'waybar' executable not found in PATH." >&2
    exit 2
fi

attempt=0
while true; do
    # If already running, nothing to do.
    if is_running "waybar"; then
        echo "waybar already running. Exiting."
        exit 0
    fi

    attempt=$((attempt + 1))
    echo "Attempt #$attempt: launching waybar..."

    # Launch waybar detached from this shell so it continues after we exit.
    # - setsid creates a new session (detaches from TTY)
    # - redirect stdin/out/err and background with &
    setsid waybar >/dev/null 2>&1 </dev/null &

    # short wait to give waybar a moment to appear in process table
    sleep "$DELAY"

    if is_running "waybar"; then
        echo "waybar is running — exiting script (will not resurrect later)."
        exit 0
    fi

    # If configured, stop after MAX_RETRIES attempts
    if [ "${MAX_RETRIES:-0}" -gt 0 ] && [ "$attempt" -ge "$MAX_RETRIES" ]; then
        echo "ERROR: reached max retries ($MAX_RETRIES) and waybar is still not running." >&2
        exit 1
    fi

    # Small backoff before next attempt (keeps fast retry behavior by default)
done
