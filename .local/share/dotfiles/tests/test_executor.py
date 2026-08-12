import tempfile
import unittest
from pathlib import Path

from dotfiles.strap.executor import StalePlanError, execute_plan
from dotfiles.strap.models import DeploymentPlan, FileOperation, OperationKind, StrapDefinition
from dotfiles.strap.planner import combine_plans, plan_strap


class NoCron:
    def read(self): return ""
    def install(self, content): pass


class ExecutorTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name); self.home = self.root / "home"; self.home.mkdir(); self.source = self.root / "source"; self.source.mkdir()

    def deployment(self, source, target, force=False):
        operation = FileOperation("strap.yaml", OperationKind.COPY, source, target, force)
        strap = StrapDefinition("strap.yaml", self.source / "strap.yaml", "Test", "Test", (operation,), ())
        return combine_plans((plan_strap(strap, home=self.home),), home=self.home, reconcile_all_cron=False)

    def test_installs_create_and_never_writes_up_to_date(self):
        source = self.source / "item"; source.write_text("value")
        target = self.home / "item"; result = execute_plan(self.deployment(source, target), cron_backend=NoCron())
        self.assertEqual(target.read_text(), "value"); self.assertEqual(len(result.completed), 1)
        result = execute_plan(self.deployment(source, target), cron_backend=NoCron())
        self.assertEqual(len(result.up_to_date), 1)

    def test_rejects_stale_target_before_mutation(self):
        source = self.source / "item"; source.write_text("wanted")
        target = self.home / "item"; plan = self.deployment(source, target); target.write_text("new")
        with self.assertRaises(StalePlanError): execute_plan(plan, cron_backend=NoCron())
        self.assertEqual(target.read_text(), "new")


if __name__ == "__main__": unittest.main()
