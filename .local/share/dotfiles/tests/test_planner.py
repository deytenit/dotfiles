import os
import tempfile
import unittest
from pathlib import Path

from dotfiles.strap.models import FileOperation, OperationKind, StrapDefinition, TargetState
from dotfiles.strap.planner import PlanningError, combine_plans, plan_strap, snapshot_path


class PlannerTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.home = self.root / "home"
        self.source = self.root / "source"
        self.home.mkdir()
        self.source.mkdir()

    def strap(self, *operations):
        return StrapDefinition("strap.yaml", self.source / "strap.yaml", "Test", "Test", tuple(operations), ())

    def test_classifies_create_current_skip_and_replace_with_snapshots(self):
        (self.source / "new").write_text("new")
        (self.source / "same").write_text("same")
        (self.source / "skip").write_text("wanted")
        (self.source / "replace").write_text("wanted")
        (self.home / "same").write_text("same")
        (self.home / "skip").write_text("other")
        (self.home / "replace").write_text("other")
        plan = plan_strap(self.strap(
            FileOperation("strap.yaml", OperationKind.COPY, self.source / "new", self.home / "new"),
            FileOperation("strap.yaml", OperationKind.COPY, self.source / "same", self.home / "same"),
            FileOperation("strap.yaml", OperationKind.COPY, self.source / "skip", self.home / "skip"),
            FileOperation("strap.yaml", OperationKind.COPY, self.source / "replace", self.home / "replace", force=True),
        ), home=self.home)

        self.assertEqual([action.state for action in plan.actions], [
            TargetState.CREATE, TargetState.UP_TO_DATE, TargetState.SKIP, TargetState.REPLACE,
        ])
        self.assertTrue(all(action.source_snapshot.kind != "absent" for action in plan.actions))
        self.assertEqual(plan.actions[0].target_snapshot.kind, "absent")

    def test_snapshots_include_modes_and_symlink_text_without_following_links(self):
        first = self.source / "first"
        second = self.source / "second"
        first.write_text("same")
        second.write_text("same")
        first.chmod(0o600)
        second.chmod(0o644)
        self.assertNotEqual(snapshot_path(first), snapshot_path(second))
        os.symlink("missing-one", self.source / "one-link")
        os.symlink("missing-two", self.source / "two-link")
        self.assertNotEqual(snapshot_path(self.source / "one-link"), snapshot_path(self.source / "two-link"))

    def test_force_directory_overlays_managed_children_and_preserves_unmanaged_children(self):
        managed = self.source / "skills"
        target = self.home / "skills"
        managed.mkdir()
        target.mkdir()
        (managed / "same").write_text("same")
        (managed / "changed").write_text("new")
        (managed / "fresh").write_text("fresh")
        (target / "same").write_text("same")
        (target / "changed").write_text("old")
        (target / "unmanaged").write_text("keep")

        plan = plan_strap(self.strap(FileOperation("strap.yaml", OperationKind.COPY, managed, target, force=True)), home=self.home)

        self.assertEqual([action.operation.target.name for action in plan.actions], ["changed", "fresh", "same"])
        self.assertEqual([action.state for action in plan.actions], [TargetState.REPLACE, TargetState.CREATE, TargetState.UP_TO_DATE])
        self.assertEqual((target / "unmanaged").read_text(), "keep")

    def test_rejects_targets_outside_home_and_duplicate_targets(self):
        source = self.source / "file"
        source.write_text("value")
        outside = self.root / "outside"
        with self.assertRaises(PlanningError):
            plan_strap(self.strap(FileOperation("strap.yaml", OperationKind.COPY, source, outside)), home=self.home)
        first = plan_strap(self.strap(FileOperation("one", OperationKind.COPY, source, self.home / "target")), home=self.home)
        second = plan_strap(self.strap(FileOperation("two", OperationKind.COPY, source, self.home / "target")), home=self.home)
        with self.assertRaises(PlanningError):
            combine_plans((first, second), home=self.home, reconcile_all_cron=False)


if __name__ == "__main__":
    unittest.main()
