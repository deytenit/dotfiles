"""Bootstrap application orchestration."""
import platform, sys
from pathlib import Path
from .cron import SystemCrontab
from .discovery import StrapValidationError, discover_straps
from .executor import ExecutionFailure, execute_plan
from .planner import PlanningError, combine_plans, plan_strap
from .ui import QuestionaryUI, UIError, render_result, render_review
from .models import SetupMode

def run_bootstrap(repo_root: Path, *, install_all: bool, stdin_is_tty=None, stdout_is_tty=None, home=None, platform_name=None, ui=None, cron_backend=None) -> int:
    home = (home or Path.home()).absolute(); name = platform_name or platform.system().lower()
    stdin_is_tty = sys.stdin.isatty() if stdin_is_tty is None else stdin_is_tty; stdout_is_tty = sys.stdout.isatty() if stdout_is_tty is None else stdout_is_tty
    if not install_all and not (stdin_is_tty and stdout_is_tty): print("Interactive setup requires a terminal. Rerun in a terminal or use --all."); return 2
    try:
        definitions = discover_straps(repo_root, home=home, platform_name=name); previews = tuple(plan_strap(item, home=home) for item in definitions)
        complete = install_all
        if install_all: selected = previews
        else:
            ui = ui or QuestionaryUI(); mode = ui.choose_mode()
            if mode is None: print("No changes made."); return 0
            complete = mode is SetupMode.COMPLETE
            if complete:
                if not ui.confirm("Set up every available configuration?"): print("No changes made."); return 0
                selected = previews
            else:
                choices = ui.choose_straps(previews)
                if choices is None: print("No changes made."); return 0
                selected = tuple(item for item in previews if item.strap.identity in choices)
        plan = combine_plans(tuple(selected), home=home, reconcile_all_cron=complete)
        print(render_review(plan, home))
        if not install_all and not ui.confirm("Apply the reviewed setup?"): print("No changes made."); return 0
        result = execute_plan(plan, cron_backend=cron_backend or SystemCrontab()); print(render_result(result, home)); return 0
    except KeyboardInterrupt: return 130
    except (StrapValidationError, PlanningError, ExecutionFailure, UIError) as error: print(error); return 1
