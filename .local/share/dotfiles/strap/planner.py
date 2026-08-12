"""Build immutable deployment plans without changing the filesystem."""

from __future__ import annotations

import hashlib
import os
import stat
from pathlib import Path

from .models import (
    DeploymentPlan,
    FileOperation,
    OperationKind,
    PlannedAction,
    StrapDefinition,
    StrapPlan,
    TargetSnapshot,
    TargetState,
)


class PlanningError(RuntimeError):
    pass


def snapshot_path(path: Path) -> TargetSnapshot:
    """Return a stable, non-following content snapshot for a filesystem entry."""
    try:
        path.lstat()
    except FileNotFoundError:
        return TargetSnapshot("absent", None)
    digest = hashlib.sha256()
    _hash_entry(digest, path, Path("."))
    mode = path.lstat().st_mode
    if stat.S_ISLNK(mode):
        kind = "symlink"
    elif stat.S_ISDIR(mode):
        kind = "directory"
    elif stat.S_ISREG(mode):
        kind = "file"
    else:
        kind = "other"
    return TargetSnapshot(kind, digest.hexdigest())


def _hash_entry(digest: hashlib._Hash, path: Path, relative: Path) -> None:
    metadata = path.lstat()
    mode = metadata.st_mode
    if stat.S_ISLNK(mode):
        kind, body = b"l", os.fsencode(os.readlink(path))
    elif stat.S_ISDIR(mode):
        kind, body = b"d", b""
    elif stat.S_ISREG(mode):
        kind, body = b"f", path.read_bytes()
    else:
        kind, body = b"o", b""
    digest.update(relative.as_posix().encode() + b"\0" + kind + b"\0")
    digest.update(f"{stat.S_IMODE(mode):o}".encode() + b"\0" + body + b"\0")
    if stat.S_ISDIR(mode):
        for child in sorted(path.iterdir(), key=lambda item: item.name):
            _hash_entry(digest, child, relative / child.name)


def plan_strap(strap: StrapDefinition, *, home: Path) -> StrapPlan:
    actions: list[PlannedAction] = []
    for operation in strap.file_operations:
        source = operation.source.absolute()
        try:
            source.resolve(strict=True)
        except OSError as error:
            raise PlanningError(f"{strap.identity}: source is missing or broken: {source}") from error
        target = _validate_target(operation.target, home)
        normalized = FileOperation(operation.strap_id, operation.kind, source, target, operation.force)
        if operation.force and source.is_dir() and not source.is_symlink() and target.is_dir() and not target.is_symlink():
            for child in sorted(source.iterdir(), key=lambda item: item.name):
                child_operation = FileOperation(
                    operation.strap_id, operation.kind, child, target / child.name, True
                )
                actions.append(_plan_action(child_operation))
        else:
            details = ()
            if operation.force and source.is_dir() and not source.is_symlink():
                details = tuple(target / child.name for child in sorted(source.iterdir(), key=lambda item: item.name))
            actions.append(_plan_action(normalized, details))
    entries = tuple(f"{item.schedule} {item.command}" for item in strap.cron_operations)
    return StrapPlan(strap, tuple(actions), entries)


def _plan_action(operation: FileOperation, detail_targets: tuple[Path, ...] = ()) -> PlannedAction:
    source = snapshot_path(operation.source)
    target = snapshot_path(operation.target)
    if target.kind == "absent":
        state = TargetState.CREATE
    elif operation.kind is OperationKind.LINK:
        state = TargetState.UP_TO_DATE if _is_correct_link(operation) else TargetState.REPLACE
    elif source == target:
        state = TargetState.UP_TO_DATE
    else:
        state = TargetState.REPLACE if operation.force else TargetState.SKIP
    return PlannedAction(operation, state, source, target, detail_targets)


def _is_correct_link(operation: FileOperation) -> bool:
    target = operation.target
    if not target.is_symlink():
        return False
    try:
        return target.resolve(strict=False) == operation.source.resolve(strict=True)
    except OSError:
        return False


def _validate_target(target: Path, home: Path) -> Path:
    lexical_home = Path(os.path.normpath(str(home.absolute())))
    lexical_target = Path(os.path.normpath(str(target.absolute())))
    if lexical_target == lexical_home:
        raise PlanningError("the home directory itself cannot be a deployment target")
    resolved_home = lexical_home.resolve()
    if not _beneath(lexical_target, lexical_home) and not _beneath(lexical_target.resolve(strict=False), resolved_home):
        raise PlanningError(f"target escapes home: {target}")
    if not _beneath(lexical_target.parent.resolve(strict=False), resolved_home):
        raise PlanningError(f"target parent resolves outside home: {target}")
    current = lexical_target.parent
    while True:
        if current.exists() or current.is_symlink():
            if not current.is_dir():
                raise PlanningError(f"target has a non-directory ancestor: {current}")
        if current == lexical_home or current.parent == current:
            break
        current = current.parent
    return lexical_target


def _beneath(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def combine_plans(
    plans: tuple[StrapPlan, ...], *, home: Path, reconcile_all_cron: bool
) -> DeploymentPlan:
    actions = tuple(action for plan in plans for action in plan.actions)
    seen: set[Path] = set()
    for action in actions:
        target = action.operation.target
        if target in seen:
            raise PlanningError(f"duplicate deployment target: {target}")
        seen.add(target)
    return DeploymentPlan(
        home.resolve(),
        plans,
        actions,
        tuple((plan.strap.identity, plan.cron_entries) for plan in plans),
        reconcile_all_cron,
    )
