-- Hyprland Lua Configuration
-- Migrated from hyprland.conf to official Lua config format for Hyprland 0.56+ / 0.57+

local colors = require("colors")

------------------
---- MONITORS ----
------------------
-- See https://wiki.hypr.land/Configuring/Basics/Monitors/
hl.monitor({
    output   = "eDP-1",
    mode     = "3072x1920@120",
    position = "0x0",
    scale    = 1.5,
})

hl.monitor({
    output   = "HEADLESS-2",
    mode     = "1920x1080@60",
    position = "3072x0",
    scale    = 1.0,
})

-------------------------------
---- ENVIRONMENT VARIABLES ----
-------------------------------
-- See https://wiki.hypr.land/Configuring/Advanced-and-Cool/Environment-variables/
hl.env("XCURSOR_THEME", "phinger-cursors-dark")
hl.env("HYPRCURSOR_THEME", "phinger-cursors-dark")
hl.env("XCURSOR_SIZE", "24")
hl.env("QT_QPA_PLATFORMTHEME", "qt6ct")
hl.env("QT_STYLE_OVERRIDE", "kvantum")
hl.env("GDK_BACKEND", "wayland")
hl.env("XDG_DATA_HOME", os.getenv("HOME") .. "/.local/share")

-------------------
---- AUTOSTART ----
-------------------
-- See https://wiki.hypr.land/Configuring/Basics/Autostart/
hl.on("hyprland.start", function ()
    hl.exec_cmd("dbus-update-activation-environment --systemd WAYLAND_DISPLAY XDG_CURRENT_DESKTOP")
    hl.exec_cmd("hypridle & hyprpaper & dunst & /usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1")
    hl.exec_cmd(os.getenv("HOME") .. "/.config/hypr/scripts/waybar.sh")
    hl.exec_cmd(os.getenv("HOME") .. "/.config/hypr/scripts/wallpaper-power-monitor.sh")
    hl.exec_cmd("sleep 5 && darkman run")
    hl.exec_cmd("thunderbird")
end)

-----------------------
---- LOOK AND FEEL ----
-----------------------
-- Refer to https://wiki.hypr.land/Configuring/Basics/Variables/
hl.config({
    xwayland = {
        force_zero_scaling = true,
    },

    general = {
        gaps_in  = 3,
        gaps_out = 7,
        border_size = 3,
        col = {
            active_border   = { colors = { colors.lavender, colors.sapphire }, angle = 45 },
            inactive_border = colors.surface0,
        },
        layout = "dwindle",
        allow_tearing = false,
    },

    decoration = {
        rounding = 8,
        blur = {
            enabled = true,
            size    = 16,
            passes  = 2,
        },
        shadow = {
            enabled      = true,
            range        = 4,
            render_power = 3,
            color        = "rgba(1a1a1aee)",
        },
    },

    animations = {
        enabled = true,
    },

    dwindle = {
        preserve_split = true,
    },

    master = {
        new_status = "master",
    },

    misc = {
        force_default_wallpaper = -1,
    },

    input = {
        kb_layout  = "us,ru",
        kb_variant = "",
        kb_model   = "",
        kb_options = "grp:win_space_toggle",
        kb_rules   = "",

        follow_mouse = 1,

        sensitivity = 0,

        touchpad = {
            natural_scroll = true,
        },
    },
})

--------------------
---- ANIMATIONS ----
--------------------
hl.curve("myBezier", { type = "bezier", points = { {0.05, 0.9}, {0.1, 1.05} } })

hl.animation({ leaf = "windows",     enabled = true, speed = 7,  bezier = "myBezier" })
hl.animation({ leaf = "windowsOut",  enabled = true, speed = 7,  bezier = "default", style = "popin 80%" })
hl.animation({ leaf = "border",      enabled = true, speed = 10, bezier = "default" })
hl.animation({ leaf = "borderangle", enabled = true, speed = 8,  bezier = "default" })
hl.animation({ leaf = "fade",        enabled = true, speed = 7,  bezier = "default" })
hl.animation({ leaf = "workspaces",  enabled = true, speed = 6,  bezier = "default" })

------------------
---- GESTURES ----
------------------
hl.gesture({
    fingers   = 3,
    direction = "horizontal",
    action    = "workspace",
})

-----------------
---- DEVICES ----
-----------------
hl.device({
    name        = "epic-mouse-v1",
    sensitivity = -0.5,
})

----------------------
---- WINDOW RULES ----
----------------------
-- Global Maximize Event Suppression
hl.window_rule({
    name           = "suppress-maximize-events",
    match          = { class = ".*" },
    suppress_event = "maximize",
})

-- Idle Inhibition
hl.window_rule({
    name         = "idle-inhibit-fullscreen",
    match        = { fullscreen = true },
    idle_inhibit = "fullscreen",
})

-- Firefox Picture-in-Picture
hl.window_rule({
    name           = "firefox-pip-overlay",
    match          = {
        class = "(f|F)irefox.*",
        title = "Picture-in-Picture",
    },
    float          = true,
    pin            = true,
    suppress_event = "fullscreen maximize",
})

---------------------
---- KEYBINDINGS ----
---------------------
local mainMod    = "SUPER"
local terminal   = "ghostty"
local browser    = "firefox-beta"
local explorer   = "nautilus"
local launcher   = "sh " .. os.getenv("HOME") .. "/.config/rofi/bin/launcher"
local powermenu  = "sh " .. os.getenv("HOME") .. "/.config/rofi/bin/powermenu"
local screenshot = "sh " .. os.getenv("HOME") .. "/.config/rofi/bin/screenshot"

-- App Launchers & Window Management
hl.bind(mainMod .. " + Q",      hl.dsp.exec_cmd(terminal))
hl.bind(mainMod .. " + W",      hl.dsp.exec_cmd(browser))
hl.bind(mainMod .. " + E",      hl.dsp.exec_cmd(explorer))
hl.bind(mainMod .. " + R",      hl.dsp.exec_cmd(launcher))
hl.bind(mainMod .. " + M",      hl.dsp.exec_cmd(powermenu))
hl.bind(mainMod .. " + print",  hl.dsp.exec_cmd(screenshot))
hl.bind(mainMod .. " + C",      hl.dsp.window.close())
hl.bind(mainMod .. " + ESCAPE", hl.dsp.exit())
hl.bind(mainMod .. " + D",      hl.dsp.window.pseudo())
hl.bind(mainMod .. " + F",      hl.dsp.window.float({ action = "toggle" }))
hl.bind(mainMod .. " + S",      hl.dsp.layout("togglesplit"))
hl.bind(mainMod .. " + V",      hl.dsp.window.fullscreen())

-- Focus with arrow keys
hl.bind(mainMod .. " + left",  hl.dsp.focus({ direction = "left" }))
hl.bind(mainMod .. " + right", hl.dsp.focus({ direction = "right" }))
hl.bind(mainMod .. " + up",    hl.dsp.focus({ direction = "up" }))
hl.bind(mainMod .. " + down",  hl.dsp.focus({ direction = "down" }))

-- Focus with HJKL
hl.bind(mainMod .. " + H", hl.dsp.focus({ direction = "left" }))
hl.bind(mainMod .. " + L", hl.dsp.focus({ direction = "right" }))
hl.bind(mainMod .. " + K", hl.dsp.focus({ direction = "up" }))
hl.bind(mainMod .. " + J", hl.dsp.focus({ direction = "down" }))

-- Workspaces 1-10
for i = 1, 10 do
    local key = i % 10 -- 10 maps to key 0
    hl.bind(mainMod .. " + " .. key,         hl.dsp.focus({ workspace = i }))
    hl.bind(mainMod .. " + SHIFT + " .. key, hl.dsp.window.move({ workspace = i }))
end

-- Relative workspace movement
hl.bind(mainMod .. " + SHIFT + N", hl.dsp.window.move({ workspace = "e+1" }))
hl.bind(mainMod .. " + SHIFT + P", hl.dsp.window.move({ workspace = "e-1" }))

hl.bind(mainMod .. " + N", hl.dsp.focus({ workspace = "e+1" }))
hl.bind(mainMod .. " + P", hl.dsp.focus({ workspace = "e-1" }))

-- Special workspace (scratchpad)
hl.bind(mainMod .. " + A",         hl.dsp.workspace.toggle_special("magic"))
hl.bind(mainMod .. " + SHIFT + A", hl.dsp.window.move({ workspace = "special:magic" }))

-- Mouse scroll through workspaces
hl.bind(mainMod .. " + mouse_down", hl.dsp.focus({ workspace = "e+1" }))
hl.bind(mainMod .. " + mouse_up",   hl.dsp.focus({ workspace = "e-1" }))

-- Mouse drag/resize
hl.bind(mainMod .. " + mouse:272", hl.dsp.window.drag(),   { mouse = true })
hl.bind(mainMod .. " + mouse:273", hl.dsp.window.resize(), { mouse = true })

-- Brightness control
hl.bind("XF86MonBrightnessUp",   hl.dsp.exec_cmd("brightnessctl s +5%"))
hl.bind("XF86MonBrightnessDown", hl.dsp.exec_cmd("brightnessctl s 5%-"))

-- Volume and Media Control
hl.bind("XF86AudioRaiseVolume", hl.dsp.exec_cmd("pamixer -i 5"))
hl.bind("XF86AudioLowerVolume", hl.dsp.exec_cmd("pamixer -d 5"))
hl.bind("XF86AudioMicMute",     hl.dsp.exec_cmd("pamixer --default-source -t"))
hl.bind("XF86AudioMute",        hl.dsp.exec_cmd("pamixer -t"))
hl.bind("XF86AudioPlay",        hl.dsp.exec_cmd("playerctl play-pause"))
hl.bind("XF86AudioPause",       hl.dsp.exec_cmd("playerctl play-pause"))
hl.bind("XF86AudioNext",        hl.dsp.exec_cmd("playerctl next"))
hl.bind("XF86AudioPrev",        hl.dsp.exec_cmd("playerctl previous"))

-- Color picker
hl.bind(mainMod .. " + X", hl.dsp.exec_cmd("hyprpicker -a"))

-- Screenshot
hl.bind("print", hl.dsp.exec_cmd("grimblast --notify copysave screen \"$HOME/Pictures/Screenshots/$(date +'%Y-%m-%d-%H%M%S.%3N.png')\""))
