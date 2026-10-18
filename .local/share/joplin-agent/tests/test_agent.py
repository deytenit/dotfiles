import contextlib
import copy
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import agent
import register
import server


class GuardTest(unittest.TestCase):
    def test_child_failures_use_actionable_message_without_child_secrets(self):
        with patch.object(agent.subprocess, "run") as run:
            run.return_value.returncode = 1
            run.return_value.stderr = "token=synthetic-secret-12345"
            with self.assertRaisesRegex(agent.SetupError, "Check notebook scope") as caught:
                agent.run_checked(["synthetic"], "Check notebook scope")
            self.assertNotIn("synthetic-secret", str(caught.exception))

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = self.root / "private"
        self.policy = agent.make_policy("work")
        self.credentials = {"token": "synthetic-secret-12345", "host": "127.0.0.1",
                            "port": 41184, "timeout": 15, "verify_ssl": False}
        agent.atomic_private(self.config / "policy.json", json.dumps(self.policy))
        agent.atomic_private(self.config / "server.json", json.dumps(self.credentials))

    def test_missing_null_empty_or_invalid_rules_stop_launch_before_exec(self):
        for rules in (None, [], [""], ["!Work"], ["Work,**"], ["Work\n**"]):
            with self.subTest(rules=rules), patch.object(agent.os, "execve") as execute:
                policy = {**self.policy, "notebook_allowlist": rules}
                agent.atomic_private(self.config / "policy.json", json.dumps(policy))
                with self.assertRaises(agent.SetupError):
                    agent.launch(self.config, self.root / "runtime")
                execute.assert_not_called()
        (self.config / "policy.json").unlink()
        with self.assertRaises(agent.SetupError):
            agent.launch(self.config, self.root / "runtime")

    def test_inherited_environment_cannot_broaden_access_or_redirect_credentials(self):
        with patch.dict(os.environ, {"JOPLIN_TOKEN": "wrong-secret", "JOPLIN_NOTEBOOK_ALLOWLIST": "**",
                                    "JOPLIN_TOOL_DELETE_NOTE": "true", "JOPLIN_HOST": "remote.test",
                                    "JOPLIN_MCP_CONFIG": "/wrong.json", "PYTHONPATH": "/untrusted",
                                    "HTTPS_PROXY": "https://proxy.test"}):
            environment = agent.child_environment(self.policy)
        self.assertEqual(environment["JOPLIN_NOTEBOOK_ALLOWLIST"], "/Work")
        self.assertEqual(environment["JOPLIN_TOOL_DELETE_NOTE"], "false")
        for name in ("JOPLIN_TOKEN", "JOPLIN_HOST", "JOPLIN_MCP_CONFIG", "PYTHONPATH", "HTTPS_PROXY"):
            self.assertNotIn(name, environment)
        self.assertEqual(environment["NO_PROXY"], "localhost,127.0.0.1")

    def test_serve_replaces_process_with_isolated_interpreter_and_no_token_argument(self):
        runtime = self.root / "runtime"
        (runtime / "bin").mkdir(parents=True)
        (runtime / "bin/python").touch()
        with patch.object(agent.os, "execve") as execute, patch.object(agent.os, "chdir"):
            agent.launch(self.config, runtime)
        executable, argv, environment = execute.call_args.args
        self.assertEqual(executable, runtime / "bin/python")
        self.assertEqual(argv[1], "-I")
        self.assertEqual(argv[-1], str(self.config))
        self.assertNotIn(self.credentials["token"], json.dumps([argv, environment]))

    def test_unsafe_permissions_symlinks_and_checkout_destinations_are_rejected(self):
        file = self.config / "policy.json"
        file.chmod(0o644)
        with self.assertRaises(agent.SetupError):
            agent.load_policy(self.config)
        file.chmod(0o600)
        file.rename(self.config / "other.json")
        file.symlink_to(self.config / "other.json")
        with self.assertRaises(agent.SetupError):
            agent.load_policy(self.config)
        file.unlink()
        (self.config / ".git").mkdir()
        with self.assertRaises(agent.SetupError):
            agent.atomic_private(file, "{}")

    def test_context_reads_no_credentials_and_reports_policy(self):
        (self.config / "server.json").unlink()
        output = io.StringIO()
        with patch.object(agent, "locations", return_value=(self.config, self.root)), patch.object(sys, "argv", ["joplin-agent", "context"]), contextlib.redirect_stdout(output):
            self.assertEqual(agent.main(), 0)
        self.assertEqual(json.loads(output.getvalue())["hierarchy"]["inbox"], "Work/Agent Inbox")
        self.assertNotIn("token", output.getvalue())

    def test_home_cache_directory_does_not_make_private_settings_a_checkout(self):
        (self.root / ".arc").mkdir()
        self.assertEqual(agent.load_policy(self.config)["notebook_allowlist"], ["/Work"])

    def test_credential_errors_never_echo_the_secret(self):
        credentials = {**self.credentials, "host": self.credentials["token"]}
        agent.atomic_private(self.config / "server.json", json.dumps(credentials))
        with self.assertRaises(agent.SetupError) as caught:
            agent.load_server(self.config)
        self.assertNotIn(self.credentials["token"], str(caught.exception))

    def test_private_policy_cannot_enable_withheld_tools(self):
        policy = copy.deepcopy(self.policy)
        policy["tools"]["tag_note"] = True
        with self.assertRaises(agent.SetupError):
            agent.validate_policy(policy)

    def test_runtime_rejects_destinations_outside_notebook_scope(self):
        policy = copy.deepcopy(self.policy)
        policy["hierarchy"]["inbox"] = "Personal/Inbox"
        agent.atomic_private(self.config / "policy.json", json.dumps(policy))
        with self.assertRaisesRegex(agent.SetupError, "outside"):
            server.configure(self.config)

    def test_explicit_runtime_config_ignores_a_permissive_discovered_file(self):
        malicious = self.root / "joplin-mcp.json"
        malicious.write_text(json.dumps({"token": "other-secret", "notebook_allowlist": ["**"]}))
        with patch.dict(os.environ, {"JOPLIN_MCP_CONFIG": str(malicious)}):
            server.configure(self.config)
        from joplin_mcp.config import get_config
        self.assertEqual(get_config().notebook_allowlist, ["/Work"])
        self.assertEqual(get_config().token, self.credentials["token"])


class RegistrationTest(unittest.TestCase):
    def test_registration_cannot_rewrite_private_credentials_policy_or_runtime(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(Path, "home", return_value=Path(directory)):
            for relative in (".config/joplin-agent/server.json", ".config/joplin-agent/policy.json", ".local/share/joplin-agent/runtime/config.json"):
                path = Path(directory) / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('{"private": "preserve"}')
                with self.assertRaises(ValueError):
                    register.register_file(path, "antigravity", "/python", [])
                self.assertEqual(path.read_text(), '{"private": "preserve"}')

    def test_codex_registration_preserves_comments_and_unrelated_settings(self):
        source = '# keep this\nmodel = "existing"\n[mcp_servers.other]\ncommand = "keep"\n'
        result = register.merged(source, "codex", "/a path/python", ["-I", "/a path/agent.py", "serve"])
        self.assertIn("# keep this", result)
        data = register.tomlkit.parse(result)
        self.assertEqual(data["model"], "existing")
        self.assertEqual(data["mcp_servers"]["other"]["command"], "keep")
        self.assertEqual(data["mcp_servers"]["joplin"]["args"], ["-I", "/a path/agent.py", "serve"])
        self.assertEqual(register.merged(result, "codex", "/a path/python", ["-I", "/a path/agent.py", "serve"]), result)

    def test_antigravity_registration_preserves_other_servers(self):
        result = register.merged('{"custom": true, "mcpServers": {"other": {"command": "keep"}}}', "antigravity", "/python", ["serve"])
        data = json.loads(result)
        self.assertTrue(data["custom"])
        self.assertEqual(data["mcpServers"]["other"], {"command": "keep"})
        self.assertEqual(data["mcpServers"]["joplin"]["command"], "/python")

    def test_malformed_config_is_preserved_and_valid_change_has_private_backup(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text("{broken")
            with self.assertRaises(ValueError):
                register.register_file(path, "antigravity", "/python", [])
            self.assertEqual(path.read_text(), "{broken")
            path.write_text('{"custom": true}')
            register.register_file(path, "antigravity", "/python", [])
            backups = list(path.parent.glob("*.joplin-backup-*"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(), '{"custom": true}')
            self.assertEqual(backups[0].stat().st_mode & 0o777, 0o600)
            register.register_file(path, "antigravity", "/python", [])
            self.assertEqual(len(list(path.parent.glob("*.joplin-backup-*"))), 1)


if __name__ == "__main__":
    unittest.main()
