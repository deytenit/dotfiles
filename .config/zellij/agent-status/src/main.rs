use serde::Deserialize;
use std::collections::BTreeMap;
use zellij_tile::prelude::*;
use unicode_width::UnicodeWidthChar;

#[derive(Deserialize)]
struct AgentEvent {
    tab_id: usize,
    tab_name: String,
    agent_id: String,
    agent: String,
    state: String,
}

struct AgentState {
    agent: String,
    state: String,
}

#[derive(Default)]
struct AgentStatus {
    tabs: BTreeMap<usize, (String, BTreeMap<String, AgentState>)>,
    style: Option<Styling>,
}

impl ZellijPlugin for AgentStatus {
    fn load(&mut self, _configuration: BTreeMap<String, String>) {
        request_permission(&[PermissionType::ReadApplicationState]);
        subscribe(&[EventType::ModeUpdate]);
    }

    fn update(&mut self, event: Event) -> bool {
        if let Event::ModeUpdate(mode) = event {
            self.style = Some(mode.style.colors);
            return true;
        }
        false
    }

    fn pipe(&mut self, message: PipeMessage) -> bool {
        if message.name != "agent-status" {
            return false;
        }
        let Some(payload) = message.payload else {
            return false;
        };
        let Ok(event) = serde_json::from_str::<AgentEvent>(&payload) else {
            return false;
        };
        if !matches!(event.state.as_str(), "running" | "waiting" | "done" | "stopped" | "clear" | "seen") {
            return false;
        }
        let (name, agents) = self.tabs.entry(event.tab_id).or_default();
        *name = event.tab_name;
        match event.state.as_str() {
            "clear" => { agents.remove(&event.agent_id); }
            "seen" => { agents.retain(|_, agent| agent.state != "stopped"); }
            _ => { agents.insert(event.agent_id, AgentState { agent: event.agent, state: event.state }); }
        }
        true
    }

    fn render(&mut self, _rows: usize, cols: usize) {
        print!("{}", render_line(&self.tabs, self.style, cols));
    }
}

fn color(color: PaletteColor, background: bool) -> String {
    let code = if background { 48 } else { 38 };
    match color {
        PaletteColor::Rgb((r, g, b)) => format!("\x1b[{code};2;{r};{g};{b}m"),
        PaletteColor::EightBit(index) => format!("\x1b[{code};5;{index}m"),
    }
}

fn clipped(text: &str, max_width: usize) -> (String, usize) {
    let mut result = String::new();
    let mut width = 0;
    for ch in text.chars().filter(|ch| !ch.is_control()) {
        let char_width = ch.width().unwrap_or(0);
        if width + char_width > max_width {
            break;
        }
        result.push(ch);
        width += char_width;
    }
    (result, width)
}

fn fill(output: &mut String, style: Option<Styling>, width: usize) {
    if let Some(theme) = style {
        let background = theme.text_unselected.background;
        output.push_str(&color(background, true));
        output.push_str(&color(background, false));
        output.push_str(&"█".repeat(width));
    } else {
        output.push_str(&" ".repeat(width));
    }
}

fn render_line(
    tabs: &BTreeMap<usize, (String, BTreeMap<String, AgentState>)>,
    style: Option<Styling>,
    cols: usize,
) -> String {
    let mut segments = Vec::new();
    for (name, agents) in tabs.values() {
        if agents.is_empty() {
            continue;
        }
        let (symbol, emphasis) = if agents.values().any(|agent| agent.state == "waiting") {
            ("?", 0)
        } else if agents.values().any(|agent| agent.state == "running") {
            ("~", 1)
        } else if agents.values().any(|agent| agent.state == "stopped") {
            ("!", 3)
        } else {
            ("*", 2)
        };
        let agent_names = agents.values().map(|agent| agent.agent.as_str()).collect::<Vec<_>>().join(",");
        segments.push((format!(" {name} {symbol} {agent_names} "), Some(emphasis)));
    }

    let mut output = String::new();
    let badge_width = if cols >= 9 { 9 } else { 0 };
    let prefix_width = 21.min(cols - badge_width);
    let (title, title_width) = clipped(" Harness      ", prefix_width);
    if let Some(theme) = style {
        output.push_str(&color(theme.text_unselected.base, false));
        output.push_str(&color(theme.text_unselected.background, true));
    }
    output.push_str("\x1b[1m");
    output.push_str(&title);
    let (status, status_width) = clipped("STATUS", prefix_width - title_width);
    if let Some(theme) = style {
        output.push_str(&color(theme.ribbon_selected.background, false));
    }
    output.push_str(&status);
    output.push_str("\x1b[22m");
    fill(&mut output, style, prefix_width - title_width - status_width);

    let mut remaining = cols - prefix_width - badge_width;
    let background = style.map(|theme| theme.text_unselected.background);
    let mut previous_bg = background;
    for (index, (text, emphasis)) in segments.iter().enumerate() {
        if remaining <= if index > 0 { 4 } else { 1 } {
            break;
        }
        let colors = style.map(|theme| {
            let ribbon = theme.ribbon_unselected;
            let background = match emphasis {
                Some(0) => ribbon.emphasis_0,
                Some(1) => ribbon.emphasis_1,
                Some(2) => ribbon.emphasis_2,
                Some(3) => ribbon.emphasis_3,
                _ => ribbon.background,
            };
            (ribbon.base, background)
        });
        if index > 0 {
            if let (Some(previous), Some(gap_bg)) = (previous_bg, background) {
                output.push_str(&color(previous, false));
                output.push_str(&color(gap_bg, true));
            }
            output.push('');
            fill(&mut output, style, 2);
            remaining -= 3;
            previous_bg = background;
        }
        if let (Some(previous), Some((_, next_bg))) = (previous_bg, colors) {
            output.push_str(&color(previous, false));
            output.push_str(&color(next_bg, true));
        }
        output.push('');
        remaining -= 1;
        if let Some((foreground, background)) = colors {
            output.push_str(&color(foreground, false));
            output.push_str(&color(background, true));
            previous_bg = Some(background);
        }
        let (visible, width) = clipped(text, remaining);
        output.push_str(&visible);
        remaining -= width;
    }
    if remaining > 0 {
        if let (Some(previous), Some(background)) = (previous_bg, background) {
            if previous != background {
                output.push_str(&color(previous, false));
                output.push_str(&color(background, true));
                output.push('');
                remaining -= 1;
            }
        }
        fill(&mut output, style, remaining);
        previous_bg = background;
    }
    if badge_width > 0 {
        if let Some(theme) = style {
            let green = theme.ribbon_selected.background;
            output.push_str(&color(previous_bg.unwrap_or(theme.text_unselected.background), false));
            output.push_str(&color(green, true));
            output.push('');
            output.push_str(&color(theme.ribbon_selected.base, false));
            output.push_str(&color(green, true));
            output.push_str("\x1b[1m");
            output.push_str("  AI  ");
            output.push_str("\x1b[22m");
            output.push_str(&color(green, false));
            output.push_str(&color(theme.text_unselected.background, true));
            output.push('');
            output.push(' ');
        } else {
            output.push_str("\x1b[1m  AI  \x1b[22m ");
        }
    }
    output.push_str("\x1b[0m");
    output
}

register_plugin!(AgentStatus);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn renders_powerline_segments_with_width_limit() {
        let mut tabs = BTreeMap::new();
        let mut agents = BTreeMap::new();
        agents.insert("codex".to_string(), AgentState { agent: "Codex".to_string(), state: "running".to_string() });
        tabs.insert(1, ("work".to_string(), agents));

        assert_eq!(render_line(&tabs, None, 40), "\u{1b}[1m Harness      STATUS\u{1b}[22m  work ~ C\u{1b}[1m  AI  \u{1b}[22m \u{1b}[0m");
        assert_eq!(render_line(&tabs, None, 8), "\u{1b}[1m Harness\u{1b}[22m\u{1b}[0m");
        assert_eq!(render_line(&tabs, None, 2), "\u{1b}[1m H\u{1b}[22m\u{1b}[0m");
    }

    #[test]
    fn separates_statuses_for_multiple_tabs() {
        let mut tabs = BTreeMap::new();
        for (id, name) in [(1, "one"), (2, "two")] {
            let mut agents = BTreeMap::new();
            agents.insert("codex".to_string(), AgentState { agent: "Codex".to_string(), state: "done".to_string() });
            tabs.insert(id, (name.to_string(), agents));
        }

        let plain = render_line(&tabs, None, 80);
        assert!(plain.starts_with("\u{1b}[1m Harness      STATUS\u{1b}[22m  one * Codex    two * Codex "));
        assert!(plain.ends_with("\u{1b}[1m  AI  \u{1b}[22m \u{1b}[0m"));

        let mut style = Styling::default();
        style.text_unselected.background = PaletteColor::Rgb((38, 38, 38));
        let line = render_line(&tabs, Some(style), 80);
        assert!(line.contains("\u{1b}[48;2;38;38;38m\u{1b}[38;2;38;38;38m██"));
    }

    #[test]
    fn clips_wide_characters_by_terminal_columns() {
        assert_eq!(clipped("界a", 2), ("界".to_string(), 2));
        assert_eq!(clipped("\u{1b}A", 1), ("A".to_string(), 1));
    }

    #[test]
    fn uses_the_active_theme_for_background_colors() {
        let mut light = Styling::default();
        light.ribbon_selected.background = PaletteColor::Rgb((20, 30, 40));
        light.text_unselected.background = PaletteColor::Rgb((246, 246, 246));
        let mut dark = Styling::default();
        dark.ribbon_selected.background = PaletteColor::Rgb((40, 30, 20));
        dark.text_unselected.background = PaletteColor::Rgb((38, 38, 38));
        let tabs = BTreeMap::new();

        let light_line = render_line(&tabs, Some(light), 40);
        let dark_line = render_line(&tabs, Some(dark), 40);
        assert!(light_line.contains("\u{1b}[38;2;20;30;40mSTATUS\u{1b}[22m"));
        assert!(dark_line.contains("\u{1b}[38;2;40;30;20mSTATUS\u{1b}[22m"));
        assert!(light_line.contains("\u{1b}[38;2;246;246;246m\u{1b}[48;2;20;30;40m"));
        assert!(dark_line.contains("\u{1b}[38;2;38;38;38m\u{1b}[48;2;40;30;20m"));
        assert!(light_line.contains("\u{1b}[1m  AI  \u{1b}[22m\u{1b}[38;2;20;30;40m\u{1b}[48;2;246;246;246m "));
        assert!(dark_line.contains("\u{1b}[1m  AI  \u{1b}[22m\u{1b}[38;2;40;30;20m\u{1b}[48;2;38;38;38m "));
    }

    #[test]
    fn theme_update_replaces_the_previous_palette() {
        let mut plugin = AgentStatus::default();
        let mut light = ModeInfo::default();
        light.style.colors.ribbon_selected.background = PaletteColor::Rgb((20, 30, 40));
        let mut dark = ModeInfo::default();
        dark.style.colors.ribbon_selected.background = PaletteColor::Rgb((40, 30, 20));

        assert!(plugin.update(Event::ModeUpdate(light)));
        assert!(render_line(&plugin.tabs, plugin.style, 20).contains("\u{1b}[48;2;20;30;40m"));
        assert!(plugin.update(Event::ModeUpdate(dark)));
        assert!(render_line(&plugin.tabs, plugin.style, 20).contains("\u{1b}[48;2;40;30;20m"));
    }

    #[test]
    fn fills_the_remaining_columns_with_the_active_theme_background() {
        let mut light = Styling::default();
        light.text_unselected.background = PaletteColor::Rgb((246, 246, 246));
        let mut dark = Styling::default();
        dark.text_unselected.background = PaletteColor::Rgb((38, 38, 38));
        let tabs = BTreeMap::new();

        let light_line = render_line(&tabs, Some(light), 10);
        let dark_line = render_line(&tabs, Some(dark), 10);
        assert!(light_line.contains("\u{1b}[48;2;246;246;246m"));
        assert!(dark_line.contains("\u{1b}[48;2;38;38;38m"));
        assert!(light_line.contains("  AI  "));
        assert!(dark_line.contains("  AI  "));
        assert!(light_line.ends_with(" \u{1b}[0m"));
        assert!(dark_line.ends_with(" \u{1b}[0m"));
        assert!(!light_line.contains("\u{1b}[0K"));
        assert!(!dark_line.contains("\u{1b}[0K"));
    }
}
