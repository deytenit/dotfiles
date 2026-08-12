import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / ".local/share"))
from dotfiles.strap.discovery import discover_straps


class RepositoryStrapsTest(unittest.TestCase):
    def test_repository_validates_on_linux_and_darwin_without_legacy_names(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory) / "home"; home.mkdir()
            linux = discover_straps(ROOT, home=home, platform_name="linux")
            darwin = discover_straps(ROOT, home=home, platform_name="darwin")
        self.assertEqual({item.category for item in linux}, {"Agent Harness", "CLI", "Desktop", "Editor", "Shell", "Terminal", "System"})
        self.assertEqual(len([item for item in linux if item.name == "Rofi"]), 1)
        self.assertNotIn("Rofi", {item.name for item in darwin})
        self.assertFalse(any(re.search(r"strap@|\.strap$", path.name) for path in ROOT.rglob("*")))
        harness = {item.name: item for item in linux if item.category == "Agent Harness"}
        self.assertEqual(set(harness), {"OpenCode", "Shared skills", "Shared instructions", "Codex agents"})
        self.assertEqual(
            {op.target.as_posix() for op in harness["Shared skills"].file_operations},
            {
                str(home / ".config/opencode/skills"),
                str(home / ".agents/skills"),
                str(home / ".claude/skills"),
            },
        )
        self.assertEqual({op.target.as_posix() for op in harness["Shared instructions"].file_operations}, {str(home / ".config/opencode/AGENTS.md"), str(home / ".codex/AGENTS.md"), str(home / ".claude/CLAUDE.md"), str(home / ".gemini/GEMINI.md")})


if __name__ == "__main__": unittest.main()
