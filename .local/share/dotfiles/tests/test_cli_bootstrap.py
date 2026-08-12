import sys
import unittest
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cli.commands.bootstrap import BootstrapCommand


class BootstrapCommandTest(unittest.TestCase):
    @patch("cli.commands.bootstrap.GitRepository")
    @patch("cli.commands.bootstrap.os.chdir")
    @patch("cli.commands.bootstrap.subprocess.run")
    def test_forwards_all_only_when_requested(self, run, chdir, repository):
        root = Path.cwd()
        repository.return_value.repo_root = root
        run.return_value.returncode = 0
        command = BootstrapCommand(Namespace(repo_root=root, all=True, quiet=True))
        with patch.object(command, "notify"):
            self.assertEqual(command.execute(), 0)
        self.assertEqual(run.call_args.args[0], [sys.executable, str(root / "bootstrap.py"), "--all"])


if __name__ == "__main__":
    unittest.main()
