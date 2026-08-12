import unittest

from dotfiles.strap.cron import CronError, apply_cron_plan, begin_marker, end_marker, render_crontab
from dotfiles.strap.models import DeploymentPlan


class FakeCrontab:
    def __init__(self, content, fail=False):
        self.content, self.fail, self.installs = content, fail, []

    def read(self):
        return self.content

    def install(self, content):
        self.installs.append(content)
        if self.fail:
            self.fail = False
            raise RuntimeError("nope")
        self.content = content


class CronTest(unittest.TestCase):
    def test_partial_updates_only_selected_section(self):
        current = "prelude\n" + begin_marker("one") + "\nold\n" + end_marker("one") + "\n" + begin_marker("two") + "\ntwo\n" + end_marker("two") + "\npostlude\n"
        actual = render_crontab(current, {"one": ("new",)}, reconcile_all=False)
        self.assertIn("new", actual)
        self.assertIn(begin_marker("two") + "\ntwo", actual)
        self.assertIn("prelude\n", actual)
        self.assertIn("postlude\n", actual)

    def test_complete_removes_all_managed_sections_and_malformed_markers_fail(self):
        current = begin_marker("old") + "\nold\n" + end_marker("old") + "\nplain\n"
        actual = render_crontab(current, {"new": ("entry",)}, reconcile_all=True)
        self.assertNotIn(begin_marker("old"), actual)
        self.assertIn(begin_marker("new"), actual)
        with self.assertRaises(CronError):
            render_crontab(begin_marker("broken") + "\n", {}, reconcile_all=False)

    def test_apply_rolls_back_original_on_install_failure(self):
        backend = FakeCrontab("original\n", fail=True)
        plan = DeploymentPlan.__new__(DeploymentPlan)
        object.__setattr__(plan, "cron_by_strap", (("one", ("* * * * * command",)),))
        object.__setattr__(plan, "reconcile_all_cron", False)
        with self.assertRaises(CronError):
            apply_cron_plan(plan, backend)
        self.assertEqual(backend.installs[-1], "original\n")


if __name__ == "__main__":
    unittest.main()
