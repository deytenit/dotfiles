"""Presentation boundary for interactive bootstrap."""
from collections import Counter
from pathlib import Path
from typing import Protocol
from .models import SetupMode, TargetState

class UIError(RuntimeError): pass
class BootstrapUI(Protocol):
    def choose_mode(self): ...
    def choose_straps(self, plans): ...
    def confirm(self, message): ...

def display_path(path: Path, home: Path) -> str:
    try: return "~" if path == home else "~/" + path.relative_to(home).as_posix()
    except ValueError: return str(path)

def impact_summary(plan):
    counts = Counter(action.state for action in plan.actions)
    labels = ((TargetState.CREATE,"new"),(TargetState.REPLACE,"replace"),(TargetState.UP_TO_DATE,"current"),(TargetState.SKIP,"unchanged"))
    return " · ".join(f"{counts[s]} {label}" for s,label in labels if counts[s]) or "no changes"

def render_catalog(plans, home):
    lines, category = [], None
    for plan in plans:
        if plan.strap.category != category:
            category = plan.strap.category; lines.extend(("", category))
        lines.append(f"  {plan.strap.name}: {impact_summary(plan)}")
        for action in plan.actions:
            lines.append(f"    {action.state.value.replace('_', ' ')}: {display_path(action.operation.target, home)}")
    return "\n".join(lines).lstrip()

def render_review(plan, home):
    headings = ((TargetState.CREATE, "Will create"), (TargetState.REPLACE, "Will replace"), (TargetState.UP_TO_DATE, "Already set up"), (TargetState.SKIP, "Will leave unchanged"))
    lines = ["Setup review"]
    for state, heading in headings:
        actions = [action for action in plan.actions if action.state is state]
        if actions:
            lines.append(heading + ":")
            lines.extend(f"  {display_path(action.operation.target, home)}" for action in actions)
    for strap_id, entries in plan.cron_by_strap:
        if entries: lines.extend((f"Cron ({strap_id}):", *(f"  {entry}" for entry in entries)))
    return "\n".join(lines)

def render_result(result, home):
    lines = []
    for heading, actions in (("Set up", result.completed), ("Already set up", result.up_to_date), ("Left unchanged", result.skipped)):
        if actions: lines.extend((heading + ":", *(f"  {display_path(a.operation.target, home)}" for a in actions)))
    return "\n".join(lines)

class QuestionaryUI:
    def __init__(self):
        try:
            from dotfiles.vendor import activate_wheels
            activate_wheels(require=True)
            import questionary
            self.questionary = questionary
        except Exception as error: raise UIError("The interactive setup could not start. Check your terminal, or rerun with --all.") from error
    def choose_mode(self):
        answer = self.questionary.select(
            "How would you like to set up your dotfiles?",
            choices=[
                self.questionary.Choice("Choose configurations", value=SetupMode.CHOOSE),
                self.questionary.Choice("Set up everything", value=SetupMode.COMPLETE),
            ],
        ).ask()
        return answer
    def choose_straps(self, plans):
        choices = []
        category = None
        for plan in plans:
            if plan.strap.category != category:
                category = plan.strap.category
                choices.append(self.questionary.Separator(f"── {category} ──"))
            choices.append(self.questionary.Choice(f"{plan.strap.name} — {plan.strap.description} ({impact_summary(plan)})", value=plan.strap.identity, checked=False))
        return self.questionary.checkbox("Select configurations", choices=choices, instruction="↑/↓ move · Space select · Enter continue · Esc cancel").ask()
    def confirm(self, message): return self.questionary.confirm(message, default=False).ask()
