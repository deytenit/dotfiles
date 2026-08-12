"""Safely execute an already-reviewed deployment plan."""
from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

from .cron import CronError, apply_cron_plan
from .models import ExecutionResult, OperationKind, PlannedAction, TargetState
from .planner import _validate_target, snapshot_path


class StalePlanError(RuntimeError): pass


class ExecutionFailure(RuntimeError):
    def __init__(self, message, result, target, restored):
        self.result, self.target, self.restored = result, target, restored
        super().__init__(message)


def execute_plan(plan, *, cron_backend):
    completed, current, skipped = [], [], []
    for action in plan.actions:
        if action.state is TargetState.UP_TO_DATE: current.append(action); continue
        if action.state is TargetState.SKIP: skipped.append(action); continue
        try:
            _install(action, plan.home)
        except StalePlanError: raise
        except Exception as error:
            result = ExecutionResult(tuple(completed), tuple(current), tuple(skipped))
            raise ExecutionFailure(str(error), result, action.operation.target, False) from error
        completed.append(action)
    result = ExecutionResult(tuple(completed), tuple(current), tuple(skipped))
    try: apply_cron_plan(plan, cron_backend)
    except CronError as error: raise ExecutionFailure(str(error), result, Path(), False) from error
    return result


def _install(action: PlannedAction, home: Path):
    op, source, target = action.operation, action.operation.source, action.operation.target
    _validate_target(target, home)
    _assert_snapshots(action)
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f".{target.name}.deytefiles-", dir=target.parent) as directory:
        stage = Path(directory) / "new"
        if op.kind is OperationKind.LINK:
            os.symlink(source, stage, target_is_directory=source.is_dir())
        elif source.is_symlink():
            os.symlink(os.readlink(source), stage, target_is_directory=source.is_dir())
        elif source.is_dir():
            shutil.copytree(source, stage, symlinks=True, copy_function=shutil.copy2)
        else: shutil.copy2(source, stage)
        _validate_target(target, home); _assert_snapshots(action)
        backup = Path(directory) / "old"; had_target = target.exists() or target.is_symlink()
        if had_target: os.replace(target, backup)
        try: os.replace(stage, target)
        except Exception:
            if target.exists() or target.is_symlink(): _remove(target)
            if had_target: os.replace(backup, target)
            raise


def _assert_snapshots(action):
    if snapshot_path(action.operation.source) != action.source_snapshot or snapshot_path(action.operation.target) != action.target_snapshot:
        raise StalePlanError(f"deployment preview is stale for {action.operation.target}")


def _remove(path):
    if path.is_dir() and not path.is_symlink(): shutil.rmtree(path)
    else: path.unlink()
