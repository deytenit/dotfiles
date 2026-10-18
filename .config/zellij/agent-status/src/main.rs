use serde::{Deserialize, Serialize};
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
    #[serde(default)]
    pane_id: Option<u32>,
    #[serde(default)]
    updated_at: u64,
}

#[derive(Clone, Deserialize, Serialize)]
struct AgentState {
    agent: String,
    state: String,
    #[serde(default)]
    pane_id: Option<u32>,
    #[serde(default)]
    updated_at: u64,
}

type Tabs = BTreeMap<usize, (String, BTreeMap<String, AgentState>)>;

#[derive(Default)]
struct AgentStatus {
    tabs: Tabs,
    tab_names: Option<BTreeMap<usize, String>>,
    style: Option<Styling>,
}

impl AgentStatus {
    fn refresh_tabs(&mut self) {
        if let Some(names) = &self.tab_names {
            self.tabs.retain(|id, (name, _)| {
                if let Some(current) = names.get(id) {
                    *name = current.trim_end_matches(" ●").to_string();
                    true
                } else {
                    false
                }
            });
        }
    }
}

impl ZellijPlugin for AgentStatus {
    fn load(&mut self, _configuration: BTreeMap<String, String>) {
        request_permission(&[
            PermissionType::ReadApplicationState,
            PermissionType::MessageAndLaunchOtherPlugins,
        ]);
        subscribe(&[EventType::ModeUpdate, EventType::TabUpdate, EventType::PermissionRequestResult]);
    }

    fn update(&mut self, event: Event) -> bool {
        match event {
            Event::ModeUpdate(mode) => {
                self.style = Some(mode.style.colors);
                return true;
            }
            Event::PermissionRequestResult(PermissionStatus::Granted) => {
                pipe_message_to_plugin(MessageToPlugin::new("agent-status-sync-request"));
            }
            Event::TabUpdate(tabs) => {
                self.tab_names = Some(tabs.into_iter().map(|tab| (tab.tab_id, tab.name)).collect());
                self.refresh_tabs();
                return true;
            }
            _ => {}
        }
        false
    }

    fn pipe(&mut self, message: PipeMessage) -> bool {
        if let PipeSource::Plugin(source) = message.source {
            if message.name == "agent-status-sync-request" {
                pipe_message_to_plugin(
                    MessageToPlugin::new("agent-status-sync")
                        .with_destination_plugin_id(source)
                        .with_payload(serde_json::to_string(&self.tabs).unwrap()),
                );
                return false;
            }
            if message.name == "agent-status-sync" {
                if let Some(tabs) = message.payload.and_then(|p| serde_json::from_str::<Tabs>(&p).ok()) {
                    merge_tabs(&mut self.tabs, tabs);
                    self.refresh_tabs();
                    return true;
                }
                return false;
            }
        }
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
        if event.state == "seen" {
            for agent in agents.values_mut() {
                if agent.state == "stopped" && agent.updated_at <= event.updated_at {
                    agent.state = "clear".to_string();
                    agent.updated_at = event.updated_at;
                }
            }
        } else if agents.get(&event.agent_id).is_none_or(|a| a.updated_at <= event.updated_at) {
            agents.insert(event.agent_id, AgentState {
                agent: event.agent, state: event.state, updated_at: event.updated_at,
                pane_id: event.pane_id,
            });
        }
        self.refresh_tabs();
        true
    }

    fn render(&mut self, _rows: usize, cols: usize) {
        print!("{}", render_line(&self.tabs, self.style, cols));
    }
}

fn merge_tabs(tabs: &mut Tabs, snapshot: Tabs) {
    for (tab_id, (name, agents)) in snapshot {
        let (_, current) = tabs.entry(tab_id).or_insert_with(|| (name, BTreeMap::new()));
        for (id, agent) in agents {
            if current.get(&id).is_none_or(|a| a.updated_at < agent.updated_at) {
                current.insert(id, agent);
            }
        }
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
        for agent in agents.values().filter(|agent| agent.state != "clear") {
            let (symbol, emphasis) = match agent.state.as_str() {
                "waiting" => ("?", 0),
                "running" => ("~", 1),
                "stopped" => ("!", 3),
                _ => ("*", 2),
            };
            let pane = agent.pane_id.map(|id| id.to_string()).unwrap_or_else(|| "?".into());
            segments.push((format!(" {name} : {pane} {symbol} {} ", agent.agent), Some(emphasis)));
        }
    }

    let mut output = String::new();
    let badge_width = if cols >= 9 { 9 } else { 0 };
    let prefix_width = 16.min(cols - badge_width);
    let (title, title_width) = clipped(" Harness ", prefix_width);
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
        if remaining <= if index > 0 { 2 } else { 1 } {
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
            if let (Some(previous), Some(background)) = (previous_bg, background) {
                output.push_str(&color(previous, false));
                output.push_str(&color(background, true));
            }
            output.push('');
            remaining -= 1;
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

    fn publish(plugin: &mut AgentStatus, tab: usize, agent: &str, state: &str, updated_at: u64) {
        assert!(plugin.pipe(PipeMessage::new(
            PipeSource::Cli("test".into()),
            "agent-status",
            &Some(serde_json::json!({
                "tab_id": tab, "tab_name": format!("tab-{tab}"),
                "agent_id": agent, "agent": agent, "state": state,
                "updated_at": updated_at, "pane_id": tab,
            }).to_string()),
            &None,
            false,
        )));
    }

    fn synchronize(destination: &mut AgentStatus, source: &AgentStatus) {
        assert!(destination.pipe(PipeMessage::new(
            PipeSource::Plugin(1), "agent-status-sync",
            &Some(serde_json::to_string(&source.tabs).unwrap()), &None, true,
        )));
    }

    #[test]
    fn sessions_in_one_tab_keep_their_panes_and_independent_states_after_sync() {
        let mut existing = AgentStatus::default();
        for (pane, state) in [(16, "running"), (17, "waiting")] {
            assert!(existing.pipe(PipeMessage::new(
                PipeSource::Cli("test".into()), "agent-status",
                &Some(serde_json::json!({
                    "tab_id": 10, "tab_name": "work", "pane_id": pane,
                    "agent_id": format!("codex:{pane}"), "agent": "Codex",
                    "state": state, "updated_at": 1,
                }).to_string()), &None, false,
            )));
        }
        let mut new_tab = AgentStatus::default();
        synchronize(&mut new_tab, &existing);
        let line = render_line(&new_tab.tabs, None, 100);
        assert!(line.contains("work : 16 ~ Codex"), "{line}");
        assert!(line.contains("work : 17 ? Codex"), "{line}");
        publish(&mut new_tab, 10, "codex:16", "clear", 2);
        let line = render_line(&new_tab.tabs, None, 100);
        assert!(!line.contains(": 16"), "{line}");
        assert!(line.contains(": 17 ? Codex"), "{line}");
    }

    #[test]
    fn legacy_events_display_an_unknown_pane_instead_of_guessing() {
        let mut plugin = AgentStatus::default();
        plugin.pipe(PipeMessage::new(
            PipeSource::Cli("test".into()), "agent-status",
            &Some(serde_json::json!({
                "tab_id": 1, "tab_name": "work", "agent_id": "codex:1",
                "agent": "Codex", "state": "running",
            }).to_string()), &None, false,
        ));
        assert!(render_line(&plugin.tabs, None, 80).contains("work : ? ~ Codex"));
    }

    #[test]
    fn new_tab_recovers_status_from_other_tabs_and_keeps_live_updates() {
        let mut existing = AgentStatus::default();
        publish(&mut existing, 1, "Codex", "running", 1);
        publish(&mut existing, 2, "Claude", "waiting", 2);
        let mut new_tab = AgentStatus::default();
        publish(&mut new_tab, 3, "Gemini", "done", 3);
        synchronize(&mut new_tab, &existing);

        let line = render_line(&new_tab.tabs, None, 100);
        for status in ["tab-1 : 1 ~ Codex", "tab-2 : 2 ? Claude", "tab-3 : 3 * Gemini"] {
            assert!(line.contains(status), "{line}");
        }
        publish(&mut new_tab, 1, "Codex", "done", 4);
        assert!(render_line(&new_tab.tabs, None, 100).contains("tab-1 : 1 * Codex"));
    }

    #[test]
    fn delayed_snapshots_do_not_restore_cleared_or_outdated_status() {
        let mut stale = AgentStatus::default();
        publish(&mut stale, 1, "Codex", "running", 1);
        publish(&mut stale, 2, "Claude", "running", 2);
        let mut current = AgentStatus::default();
        publish(&mut current, 1, "Codex", "clear", 3);
        publish(&mut current, 2, "Claude", "done", 4);
        synchronize(&mut current, &stale);
        publish(&mut current, 2, "Claude", "running", 2);

        let line = render_line(&current.tabs, None, 100);
        assert!(!line.contains("Codex"));
        assert!(line.contains("tab-2 : 2 * Claude"));
        let mut new_tab = AgentStatus::default();
        synchronize(&mut new_tab, &stale);
        synchronize(&mut new_tab, &current);
        assert_eq!(render_line(&new_tab.tabs, None, 100), line);
    }

    #[test]
    fn seen_stopped_agents_stay_cleared_after_sync() {
        let mut stale = AgentStatus::default();
        publish(&mut stale, 1, "Codex", "stopped", 1);
        let mut current = AgentStatus::default();
        synchronize(&mut current, &stale);
        publish(&mut current, 1, "", "seen", 2);
        synchronize(&mut current, &stale);
        assert!(!render_line(&current.tabs, None, 80).contains("Codex"));
    }

    #[test]
    fn closed_tabs_stay_removed_and_renamed_tabs_use_current_names() {
        let mut stale = AgentStatus::default();
        publish(&mut stale, 1, "Codex", "running", 1);
        publish(&mut stale, 2, "Claude", "waiting", 2);
        let mut current = AgentStatus::default();
        synchronize(&mut current, &stale);
        assert!(current.update(Event::TabUpdate(vec![TabInfo {
            tab_id: 2, name: "renamed ●".into(), ..Default::default()
        }])));
        synchronize(&mut current, &stale);
        let line = render_line(&current.tabs, None, 100);
        assert!(!line.contains("Codex"));
        assert!(line.contains("renamed : 2 ? Claude"));
        assert!(current.update(Event::TabUpdate(vec![])));
        synchronize(&mut current, &stale);
        assert!(!render_line(&current.tabs, None, 100).contains("Claude"));
    }

    #[test]
    fn renders_powerline_segments_with_width_limit() {
        let mut tabs = BTreeMap::new();
        let mut agents = BTreeMap::new();
        agents.insert("codex".to_string(), AgentState { agent: "Codex".to_string(), state: "running".to_string(), updated_at: 1, pane_id: Some(7) });
        tabs.insert(1, ("work".to_string(), agents));

        assert_eq!(render_line(&tabs, None, 44), "\u{1b}[1m Harness STATUS\u{1b}[22m  work : 7 ~ Codex \u{1b}[1m  AI  \u{1b}[22m \u{1b}[0m");
        assert_eq!(render_line(&tabs, None, 8), "\u{1b}[1m Harness\u{1b}[22m\u{1b}[0m");
        assert_eq!(render_line(&tabs, None, 2), "\u{1b}[1m H\u{1b}[22m\u{1b}[0m");
    }

    #[test]
    fn separates_statuses_for_multiple_tabs() {
        let mut tabs = BTreeMap::new();
        for (id, name) in [(1, "one"), (2, "two")] {
            let mut agents = BTreeMap::new();
            agents.insert("codex".to_string(), AgentState { agent: "Codex".to_string(), state: "done".to_string(), updated_at: 1, pane_id: Some(id as u32) });
            tabs.insert(id, (name.to_string(), agents));
        }

        let plain = render_line(&tabs, None, 80);
        assert!(plain.starts_with("\u{1b}[1m Harness STATUS\u{1b}[22m  one : 1 * Codex  two : 2 * Codex "));
        assert!(plain.ends_with("\u{1b}[1m  AI  \u{1b}[22m \u{1b}[0m"));

        assert_eq!(plain.matches('').count(), 5);

        let mut style = Styling::default();
        style.text_unselected.background = PaletteColor::Rgb((38, 38, 38));
        style.ribbon_unselected.emphasis_2 = PaletteColor::Rgb((100, 150, 200));
        let line = render_line(&tabs, Some(style), 80);
        assert!(line.contains(" Codex \u{1b}[38;2;100;150;200m\u{1b}[48;2;38;38;38m\u{1b}[38;2;38;38;38m\u{1b}[48;2;100;150;200m"));
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
