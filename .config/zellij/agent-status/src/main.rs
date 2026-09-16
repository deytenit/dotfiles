use serde::Deserialize;
use std::collections::BTreeMap;
use zellij_tile::prelude::*;

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
}

impl ZellijPlugin for AgentStatus {
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
            "seen" => { agents.retain(|_, agent| agent.state != "done" && agent.state != "stopped"); }
            _ => { agents.insert(event.agent_id, AgentState { agent: event.agent, state: event.state }); }
        }
        true
    }

    fn render(&mut self, _rows: usize, cols: usize) {
        let mut line = String::from("AI");
        for (name, agents) in self.tabs.values() {
            if agents.is_empty() {
                continue;
            }
            let state = if agents.values().any(|agent| agent.state == "waiting") {
                "?"
            } else if agents.values().any(|agent| agent.state == "running") {
                "~"
            } else if agents.values().any(|agent| agent.state == "stopped") {
                "!"
            } else {
                "*"
            };
            let agents = agents.values().map(|agent| agent.agent.as_str()).collect::<Vec<_>>().join(",");
            line.push_str(&format!("  {name} {state} {agents}"));
        }
        print!("{}", line.chars().take(cols).collect::<String>());
    }
}

register_plugin!(AgentStatus);
