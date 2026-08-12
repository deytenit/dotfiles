import sys
import types
import unittest
from unittest.mock import patch

from dotfiles.strap.models import SetupMode
from dotfiles.strap.models import StrapDefinition, StrapPlan
from dotfiles.strap.ui import QuestionaryUI


class FakePrompt:
    def ask(self):
        return SetupMode.CHOOSE


class UIRegressionTest(unittest.TestCase):
    def test_mode_choices_are_questionary_choice_objects(self):
        received = []
        module = types.SimpleNamespace(
            Choice=lambda title, value: {"title": title, "value": value},
            select=lambda message, choices: received.append(choices) or FakePrompt(),
        )
        with patch("dotfiles.vendor.activate_wheels"), patch.dict(sys.modules, {"questionary": module}):
            ui = QuestionaryUI()
            self.assertEqual(ui.choose_mode(), SetupMode.CHOOSE)
        self.assertEqual(received[0], [
            {"title": "Choose configurations", "value": SetupMode.CHOOSE},
            {"title": "Set up everything", "value": SetupMode.COMPLETE},
        ])

    def test_selection_groups_choices_with_separators_and_compact_trivia(self):
        received = []
        module = types.SimpleNamespace(
            Choice=lambda title, value, checked=False: {"choice": title, "value": value, "checked": checked},
            Separator=lambda title: {"separator": title},
            checkbox=lambda message, choices, instruction: received.append(choices) or FakePrompt(),
        )
        plans = (
            StrapPlan(StrapDefinition("one", __file__, "One", "Agent Harness", (), (), "Helpful tools"), (), ()),
            StrapPlan(StrapDefinition("two", __file__, "Two", "CLI", (), (), "Handy commands"), (), ()),
        )
        with patch("dotfiles.vendor.activate_wheels"), patch.dict(sys.modules, {"questionary": module}):
            ui = QuestionaryUI()
            ui.choose_straps(plans)
        self.assertEqual(received[0], [
            {"separator": "── Agent Harness ──"},
            {"choice": "One — Helpful tools (no changes)", "value": "one", "checked": False},
            {"separator": "── CLI ──"},
            {"choice": "Two — Handy commands (no changes)", "value": "two", "checked": False},
        ])


if __name__ == "__main__": unittest.main()
