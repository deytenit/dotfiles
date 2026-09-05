#!/usr/bin/env python3
"""
Hyprland Power & Profile Daemon
Seamlessly synchronizes Hyprland display settings and visuals with:
  1. Power profile changes via net.hadess.PowerProfiles (Waybar / TuneD / PPD)
  2. Power supply events (AC vs Battery) via org.freedesktop.UPower / sysfs

Profiles:
  - power-saver:
      • Display: 60Hz (3072x1920@60) - drops panel & GPU power by ~2-4W
      • Compositor: blur & shadows disabled (reduces GPU render passes)
      • Animated wallpaper: disabled (static hyprpaper wallpaper)
  - balanced:
      • Display: 120Hz (3072x1920@120) - ultra-smooth scrolling
      • Compositor: blur & shadows enabled
      • Animated wallpaper: active when on AC, static when on battery
  - performance:
      • Display: 120Hz (3072x1920@120)
      • Compositor: blur & shadows enabled
      • Animated wallpaper: active when on AC, static when on battery
"""

import os
import sys
import time
import subprocess
import signal
import gi

gi.require_version("Gio", "2.0")
gi.require_version("GLib", "2.0")
from gi.repository import Gio, GLib

LOCKFILE = "/tmp/hypr-power-daemon.lock"
LOGFILE = "/tmp/hypr-power-daemon.log"


def log(msg):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line, flush=True)
    try:
        with open(LOGFILE, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass


def notify(title, message, icon="battery-symbolic", urgency="normal"):
    try:
        subprocess.Popen(
            [
                "notify-send",
                "-a", "Power Management",
                "-i", icon,
                "-u", urgency,
                title,
                message,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        log(f"Notification error: {e}")


def hyprctl(args):
    try:
        cmd = ["hyprctl"] + args
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=3)
        return res.returncode == 0
    except Exception as e:
        log(f"hyprctl error with args {args}: {e}")
        return False


def get_current_theme_mode():
    cache_file = os.path.expanduser("~/.cache/hypr_wallpaper_mode")
    if os.path.exists(cache_file):
        try:
            with open(cache_file) as f:
                mode = f.read().strip()
                if mode in ("dark", "light"):
                    return mode
        except Exception:
            pass
    try:
        res = subprocess.run(["darkman", "get"], capture_output=True, text=True, timeout=2)
        if res.returncode == 0:
            mode = res.stdout.strip()
            if mode in ("dark", "light"):
                return mode
    except Exception:
        pass
    return "dark"


def set_animated_wallpaper(enabled):
    if not enabled:
        try:
            subprocess.run(["pkill", "-f", "linux-wallpaperengine"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass
    else:
        mode = get_current_theme_mode()
        script = os.path.expanduser("~/.config/hypr/scripts/wallpaper-engine-switcher.sh")
        if os.path.isfile(script) and os.access(script, os.X_OK):
            subprocess.Popen([script, mode], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


class PowerDaemon:
    def __init__(self):
        self.bus = Gio.bus_get_sync(Gio.BusType.SYSTEM, None)
        self.active_profile = self.get_active_profile()
        self.on_battery = self.get_on_battery()

        log(f"Initial state: profile={self.active_profile}, on_battery={self.on_battery}")

        # Subscribe to PowerProfiles PropertiesChanged (sender=None matches any unique name)
        self.bus.signal_subscribe(
            None,
            "org.freedesktop.DBus.Properties",
            "PropertiesChanged",
            "/net/hadess/PowerProfiles",
            None,
            Gio.DBusSignalFlags.NONE,
            self.on_pp_signal,
            None,
        )

        # Subscribe to UPower PropertiesChanged
        self.bus.signal_subscribe(
            None,
            "org.freedesktop.DBus.Properties",
            "PropertiesChanged",
            "/org/freedesktop/UPower",
            None,
            Gio.DBusSignalFlags.NONE,
            self.on_upower_signal,
            None,
        )

        # Apply initial tuning
        self.apply_tuning(send_notification=False)

        # Periodic check every 15 seconds
        GLib.timeout_add_seconds(15, self.periodic_check)

    def get_active_profile(self):
        try:
            proxy = Gio.DBusProxy.new_sync(
                self.bus,
                Gio.DBusProxyFlags.NONE,
                None,
                "net.hadess.PowerProfiles",
                "/net/hadess/PowerProfiles",
                "org.freedesktop.DBus.Properties",
                None,
            )
            val = proxy.call_sync(
                "Get",
                GLib.Variant("(ss)", ("net.hadess.PowerProfiles", "ActiveProfile")),
                Gio.DBusCallFlags.NONE,
                -1,
                None,
            )
            return val.unpack()[0]
        except Exception as e:
            log(f"Error fetching ActiveProfile: {e}")
            return "balanced"

    def get_on_battery(self):
        try:
            proxy = Gio.DBusProxy.new_sync(
                self.bus,
                Gio.DBusProxyFlags.NONE,
                None,
                "org.freedesktop.UPower",
                "/org/freedesktop/UPower",
                "org.freedesktop.DBus.Properties",
                None,
            )
            val = proxy.call_sync(
                "Get",
                GLib.Variant("(ss)", ("org.freedesktop.UPower", "OnBattery")),
                Gio.DBusCallFlags.NONE,
                -1,
                None,
            )
            return val.unpack()[0]
        except Exception as e:
            log(f"Error fetching OnBattery from UPower: {e}")
            return self.check_sysfs_battery()

    def check_sysfs_battery(self):
        try:
            for p in os.listdir("/sys/class/power_supply"):
                type_path = os.path.join("/sys/class/power_supply", p, "type")
                if os.path.exists(type_path):
                    with open(type_path) as f:
                        if f.read().strip() == "Mains":
                            online_path = os.path.join("/sys/class/power_supply", p, "online")
                            if os.path.exists(online_path):
                                with open(online_path) as f2:
                                    if f2.read().strip() == "1":
                                        return False
            return True
        except Exception:
            return False

    def on_pp_signal(self, conn, sender, path, iface, signal, params, user_data):
        unpacked = params.unpack()
        if len(unpacked) >= 2 and isinstance(unpacked[1], dict):
            changed_props = unpacked[1]
            if "ActiveProfile" in changed_props:
                new_profile = changed_props["ActiveProfile"]
                if new_profile != self.active_profile:
                    log(f"Power profile changed: {self.active_profile} -> {new_profile}")
                    self.active_profile = new_profile
                    self.apply_tuning(send_notification=True)

    def on_upower_signal(self, conn, sender, path, iface, signal, params, user_data):
        unpacked = params.unpack()
        if len(unpacked) >= 2 and isinstance(unpacked[1], dict):
            changed_props = unpacked[1]
            if "OnBattery" in changed_props:
                new_on_bat = changed_props["OnBattery"]
                if new_on_bat != self.on_battery:
                    log(f"Power source changed: on_battery={new_on_bat}")
                    self.on_battery = new_on_bat
                    self.handle_power_source_change()

    def handle_power_source_change(self):
        if self.on_battery:
            set_animated_wallpaper(False)
            notify(
                "Running on Battery",
                "Switched to battery power. Animated wallpaper paused.",
                icon="battery-good-symbolic",
            )
        else:
            if self.active_profile in ("balanced", "performance"):
                set_animated_wallpaper(True)
            notify(
                "Connected to AC Power",
                "Charging. Full power available.",
                icon="ac-adapter-symbolic",
            )

    def apply_tuning(self, send_notification=True):
        profile = self.active_profile or "balanced"

        if profile == "power-saver":
            # 1. 60Hz display refresh
            hyprctl(["keyword", "monitor", "eDP-1,3072x1920@60,0x0,1.5"])
            # 2. Disable blur & shadows
            hyprctl(["keyword", "decoration:blur:enabled", "false"])
            hyprctl(["keyword", "decoration:shadow:enabled", "false"])
            # 3. Disable animated wallpaper
            set_animated_wallpaper(False)

            if send_notification:
                notify(
                    "Power Saver Active",
                    "• Display: 60Hz refresh rate\n• Compositor: blur & shadows disabled\n• SoC: max efficiency (15W cap)",
                    icon="battery-good-symbolic",
                )

        elif profile == "performance":
            # 1. 120Hz display refresh
            hyprctl(["keyword", "monitor", "eDP-1,3072x1920@120,0x0,1.5"])
            # 2. Enable blur & shadows
            hyprctl(["keyword", "decoration:blur:enabled", "true"])
            hyprctl(["keyword", "decoration:shadow:enabled", "true"])
            # 3. Animated wallpaper on AC
            if not self.on_battery:
                set_animated_wallpaper(True)
            else:
                set_animated_wallpaper(False)

            if send_notification:
                notify(
                    "Performance Mode Active",
                    "• Display: 120Hz refresh rate\n• Compositor: full visual effects\n• SoC: 54W+ turbo boost unlocked",
                    icon="power-profile-performance-symbolic",
                )

        else:  # balanced
            # 1. 120Hz display refresh
            hyprctl(["keyword", "monitor", "eDP-1,3072x1920@120,0x0,1.5"])
            # 2. Enable blur & shadows
            hyprctl(["keyword", "decoration:blur:enabled", "true"])
            hyprctl(["keyword", "decoration:shadow:enabled", "true"])
            # 3. Animated wallpaper on AC
            if not self.on_battery:
                set_animated_wallpaper(True)
            else:
                set_animated_wallpaper(False)

            if send_notification:
                notify(
                    "Balanced Mode Active",
                    "• Display: 120Hz refresh rate\n• Compositor: full visual effects\n• SoC: dynamic balanced scaling",
                    icon="battery-symbolic",
                )

    def periodic_check(self):
        cur_prof = self.get_active_profile()
        if cur_prof != self.active_profile:
            log(f"Periodic check detected profile change: {self.active_profile} -> {cur_prof}")
            self.active_profile = cur_prof
            self.apply_tuning(send_notification=True)

        cur_bat = self.get_on_battery()
        if cur_bat != self.on_battery:
            log(f"Periodic check detected power source change: {self.on_battery} -> {cur_bat}")
            self.on_battery = cur_bat
            self.handle_power_source_change()

        return True


def acquire_lock():
    if os.path.exists(LOCKFILE):
        try:
            with open(LOCKFILE) as f:
                pid = int(f.read().strip())
            os.kill(pid, 0)
            print(f"Daemon already running with PID {pid}. Exiting.")
            sys.exit(0)
        except (ValueError, OSError):
            pass
    with open(LOCKFILE, "w") as f:
        f.write(str(os.getpid()))


def cleanup_lock(*args):
    try:
        os.remove(LOCKFILE)
    except Exception:
        pass
    sys.exit(0)


def main():
    acquire_lock()
    signal.signal(signal.SIGINT, cleanup_lock)
    signal.signal(signal.SIGTERM, cleanup_lock)

    log("Starting Hyprland Power & Profile Daemon...")
    daemon = PowerDaemon()

    loop = GLib.MainLoop()
    try:
        loop.run()
    except KeyboardInterrupt:
        pass
    finally:
        cleanup_lock()


if __name__ == "__main__":
    main()
