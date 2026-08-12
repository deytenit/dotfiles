import tempfile
import unittest
from pathlib import Path

from dotfiles.strap.app import run_bootstrap


ROOT = Path(__file__).resolve().parents[4]


class FakeCrontab:
    def __init__(self):
        self.content = "unmanaged entry\n"

    def read(self):
        return self.content

    def install(self, content):
        self.content = content


class BootstrapAppTest(unittest.TestCase):
    def test_all_uses_temporary_home_preserves_unmanaged_overlay_and_cron(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory) / "home"
            home.mkdir()
            unmanaged = home / ".agents/skills/unmanaged"
            unmanaged.parent.mkdir(parents=True)
            unmanaged.write_text("keep")
            cron = FakeCrontab()

            status = run_bootstrap(ROOT, install_all=True, home=home, platform_name="linux", cron_backend=cron)

            self.assertEqual(status, 0)
            self.assertEqual(unmanaged.read_text(), "keep")
            self.assertTrue((home / ".config/opencode/skills").is_dir())
            self.assertTrue((home / ".agents/skills/brainstorming/SKILL.md").is_file())
            self.assertTrue(cron.content.startswith("unmanaged entry\n"))


if __name__ == "__main__":
    unittest.main()
