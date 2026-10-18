import importlib.util
import io
import json
import os
import subprocess
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[4]
spec = importlib.util.spec_from_file_location("agent_status", ROOT / ".config/zellij/agent-status.py")
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)


class AgentStatusTest(unittest.TestCase):
    def publish(self, pane_id, event):
        tabs = [
            {"tab_id": 0, "name": "direct-modules (a)", "active": True},
            {"tab_id": 10, "name": "work", "active": False},
        ]
        panes = [
            {"id": 1, "is_plugin": False, "tab_id": 0},
            {"id": 16, "is_plugin": True, "tab_id": 0},
            {"id": 16, "is_plugin": False, "tab_id": 10},
            {"id": 17, "is_plugin": False, "tab_id": 10},
        ]
        payloads = []

        def run(args, **kwargs):
            if args[1:] == ["action", "list-panes", "--json"]:
                output = json.dumps(panes)
            elif args[1:] == ["action", "list-tabs", "--json"]:
                output = json.dumps(tabs)
            elif args[1:4] == ["pipe", "--name", "agent-status"]:
                payloads.append(json.loads(args[-1]))
                output = ""
            else:
                self.fail(f"Unexpected command: {args}")
            return subprocess.CompletedProcess(args, 0, output)

        with patch.dict(os.environ, {"ZELLIJ_PANE_ID": pane_id, "ZELLIJ_SESSION_NAME": "dev"}), \
                patch.object(bridge.subprocess, "run", side_effect=run), \
                patch.object(bridge.sys, "argv", ["agent-status.py", "codex-hook"]), \
                patch.object(bridge.sys, "stdin", io.StringIO(json.dumps(event))):
            bridge.main()
        return payloads

    def test_two_sessions_in_one_tab_publish_independent_pane_identities(self):
        first = self.publish("16", {"hook_event_name": "UserPromptSubmit", "session_id": "first"})[0]
        second = self.publish("17", {"hook_event_name": "PermissionRequest", "session_id": "second"})[0]
        self.assertEqual((first["tab_id"], first["tab_name"], first["pane_id"], first["state"]),
                         (10, "work", 16, "running"))
        self.assertEqual((second["tab_id"], second["pane_id"], second["state"]), (10, 17, "waiting"))
        self.assertNotEqual(first["agent_id"], second["agent_id"])

    def test_prefixed_pane_id_ignores_plugin_with_the_same_id(self):
        event = self.publish("terminal_16", {"hook_event_name": "Interrupt"})[0]
        self.assertEqual((event["tab_id"], event["pane_id"], event["state"]), (10, 16, "stopped"))

    def test_subagents_keep_the_parent_pane_and_their_own_identity(self):
        event = self.publish("16", {"hook_event_name": "SubagentStart", "agent_id": "child", "agent_type": "checker"})[0]
        self.assertEqual((event["pane_id"], event["agent_id"], event["agent"]),
                         (16, "codex-subagent:child", "checker"))

    def test_closed_pane_does_not_report_against_the_active_tab(self):
        self.assertEqual(self.publish("99", {"hook_event_name": "UserPromptSubmit"}), [])


@unittest.skipUnless(shutil.which("fish"), "Fish is required for launcher checks")
class CodexLauncherTest(unittest.TestCase):
    def test_zellij_sessions_get_private_servers_and_other_launches_are_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            executable = Path(directory) / "codex"
            executable.write_text("#!/usr/bin/env python3\nimport json,sys\nprint(json.dumps(sys.argv[1:]))\nsys.exit(23)\n")
            executable.chmod(0o755)
            for pane, arguments in [(None, ["resume", "session with spaces"]),
                                    ("16", ["resume", "session with spaces"]),
                                    ("17", ["--no-daemon", "resume", "second"])]:
                with self.subTest(pane=pane, arguments=arguments):
                    env = dict(os.environ, PATH=directory + os.pathsep + os.environ["PATH"])
                    env.pop("ZELLIJ_PANE_ID", None)
                    env.pop("ZELLIJ_SESSION_NAME", None)
                    if pane:
                        env.update(ZELLIJ_PANE_ID=pane, ZELLIJ_SESSION_NAME="dev")
                    result = subprocess.run(
                        [shutil.which("fish"), "--no-config", "-c", "source $argv[1]; codex $argv[2..]",
                         str(ROOT / ".config/fish/functions.fish"), *arguments],
                        env=env, capture_output=True, text=True, timeout=10,
                    )
                    self.assertEqual(result.returncode, 23, result.stderr)
                    self.assertEqual(json.loads(result.stdout),
                                     (["--no-daemon"] if pane and "--no-daemon" not in arguments else []) + arguments)


if __name__ == "__main__":
    unittest.main()
