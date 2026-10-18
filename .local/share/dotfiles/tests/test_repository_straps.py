import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / ".local/share"))
from dotfiles.strap.discovery import discover_straps
from dotfiles.strap.executor import execute_plan
from dotfiles.strap.planner import combine_plans, plan_strap
from dotfiles.strap.models import TargetState


class RepositoryStrapsTest(unittest.TestCase):
    def test_codex_configuration_is_copied_and_later_local_edits_are_preserved(self):
        class NoCron:
            def read(self): return "\n"
            def install(self, content):
                if content != "\n":
                    raise AssertionError("Config deployment must not change cron")

        for platform in ("linux", "darwin"):
            with self.subTest(platform=platform), tempfile.TemporaryDirectory() as directory:
                home = Path(directory) / "home"
                home.mkdir()
                strap = next(s for s in discover_straps(ROOT, home=home, platform_name=platform) if s.name == "Codex configuration")
                plan = combine_plans((plan_strap(strap, home=home),), home=home, reconcile_all_cron=False)
                execute_plan(plan, cron_backend=NoCron())
                target = home / ".codex/config.toml"
                self.assertFalse(target.is_symlink())
                self.assertEqual(target.read_bytes(), (ROOT / ".codex/config.base.toml").read_bytes())
                target.write_text('model = "machine-specific"\n')
                replanned = plan_strap(strap, home=home)
                self.assertEqual(replanned.actions[0].state, TargetState.SKIP)
                execute_plan(combine_plans((replanned,), home=home, reconcile_all_cron=False), cron_backend=NoCron())
                self.assertEqual(target.read_text(), 'model = "machine-specific"\n')

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
        self.assertEqual(set(harness), {"OpenCode", "Shared skills", "Shared instructions", "Codex agents", "Codex status hooks", "Gemini agents", "Joplin integration", "Codex configuration"})
        skills = ROOT / ".config/opencode/skills"
        skill_entries = {
            Path("_shared/artifact-policy.md"),
            *(path.relative_to(skills) for path in skills.iterdir() if path.is_dir() and path.name != "_shared"),
        }
        skill_targets = (
            home / ".config/opencode/skills",
            home / ".agents/skills",
            home / ".claude/skills",
            home / ".gemini/config/skills",
        )
        self.assertEqual(
            {op.target.as_posix() for op in harness["Shared skills"].file_operations},
            {str(target / entry) for target in skill_targets for entry in skill_entries},
        )
        self.assertEqual({op.target.as_posix() for op in harness["Shared instructions"].file_operations}, {str(home / ".config/opencode/AGENTS.md"), str(home / ".codex/AGENTS.md"), str(home / ".claude/CLAUDE.md"), str(home / ".gemini/GEMINI.md")})


if __name__ == "__main__": unittest.main()
