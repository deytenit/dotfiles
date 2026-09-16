#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import time


def zellij(*args):
    return subprocess.run(
        ["zellij", *args],
        capture_output=True,
        text=True,
        timeout=2,
        check=True,
    ).stdout


def current_tab():
    pane_id = os.environ.get("ZELLIJ_PANE_ID", "").removeprefix("terminal_")
    if not pane_id or not os.environ.get("ZELLIJ_SESSION_NAME"):
        return None
    for pane in json.loads(zellij("action", "list-panes", "--json")):
        if not pane["is_plugin"] and str(pane["id"]) == pane_id:
            return next(
                (tab for tab in json.loads(zellij("action", "list-tabs", "--json"))
                 if tab["tab_id"] == pane["tab_id"]),
                None,
            )
    return None


def send_pipe(tab_id, tab_name, agent_id, agent, state):
    payload = json.dumps(
        {"tab_id": tab_id, "tab_name": tab_name.removesuffix(" ●"),
         "agent_id": agent_id, "agent": agent, "state": state},
        separators=(",", ":"),
    )
    subprocess.run(
        ["zellij", "pipe", "--name", "agent-status", "--", payload],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=2,
        check=True,
    )


def watch_tab(tab_id):
    while True:
        tab = next(
            (tab for tab in json.loads(zellij("action", "list-tabs", "--json"))
             if tab["tab_id"] == tab_id),
            None,
        )
        if tab is None or not tab["name"].endswith(" ●"):
            return
        if tab["active"]:
            name = tab["name"][:-2]
            zellij("action", "rename-tab", "--tab-id", str(tab_id), name)
            send_pipe(tab_id, name, "", "", "seen")
            return
        time.sleep(1)


def send(agent_id, agent, state):
    tab = current_tab()
    if tab is None:
        return
    tab_id = tab["tab_id"]
    name = tab["name"]
    send_pipe(tab_id, name, agent_id, agent, state)
    if state == "running" and name.endswith(" ●"):
        zellij("action", "rename-tab", "--tab-id", str(tab_id), name[:-2])
    if state == "done" and not tab["active"] and not name.endswith(" ●"):
        zellij("action", "rename-tab", "--tab-id", str(tab_id), name + " ●")
        subprocess.Popen(
            [sys.executable, __file__, "watch", str(tab_id)],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )


def main():
    mode = sys.argv[1]
    if mode == "watch":
        watch_tab(int(sys.argv[2]))
    elif mode == "codex-hook":
        event = json.load(sys.stdin)
        name = event.get("hook_event_name")
        state = {
            "UserPromptSubmit": "running",
            "PermissionRequest": "waiting",
            "PostToolUse": "running",
            "Interrupt": "stopped",
            "SessionEnd": "clear",
            "SubagentStart": "running",
            "SubagentStop": "clear",
        }.get(name)
        if state is None:
            return
        if name.startswith("Subagent"):
            agent_id = event.get("agent_id")
            if not agent_id:
                return
            send(f"codex-subagent:{agent_id}", event.get("agent_type") or "subagent", state)
        else:
            send(f"codex:{os.environ.get('ZELLIJ_PANE_ID', '')}", "Codex", state)
    elif mode == "codex-notify":
        event = json.loads(sys.argv[2])
        if event.get("type") == "agent-turn-complete":
            send(f"codex:{os.environ.get('ZELLIJ_PANE_ID', '')}", "Codex", "done")
    elif mode == "emit":
        agent, state, agent_id = sys.argv[2:5]
        if state not in {"running", "waiting", "done", "stopped", "clear"}:
            raise ValueError(state)
        send(agent_id, agent, state)


if __name__ == "__main__":
    try:
        main()
    except (IndexError, ValueError, json.JSONDecodeError, OSError, subprocess.SubprocessError):
        pass
