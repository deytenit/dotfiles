import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / ".codex/config.base.toml"


def recorder(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("#!" + sys.executable + "\nimport json,sys\nprint(json.dumps(sys.argv[1:]))\n")
    path.chmod(0o755)


class CodexConfigTest(unittest.TestCase):
    def test_portable_joplin_launch_uses_home_with_spaces_without_path_lookup(self):
        config = tomllib.loads(BASE.read_text())["mcp_servers"]["joplin"]
        with tempfile.TemporaryDirectory(prefix="codex home ") as directory:
            home = Path(directory)
            recorder(home / ".local/share/joplin-agent/runtime/bin/python")
            result = subprocess.run([config["command"], *config["args"]],
                                    env={"HOME": str(home), "PATH": "/nonexistent"},
                                    capture_output=True, text=True, check=True, timeout=10)
            self.assertEqual(json.loads(result.stdout), ["-I", str(home / ".local/share/joplin-agent/app/agent.py"), "serve"])


if __name__ == "__main__":
    unittest.main()
