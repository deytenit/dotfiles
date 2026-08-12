"""Immutable values shared by strap discovery, planning, and execution."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class SetupMode(str, Enum):
    CHOOSE = "choose"
    COMPLETE = "complete"


class OperationKind(str, Enum):
    LINK = "link"
    COPY = "copy"


class TargetState(str, Enum):
    CREATE = "create"
    UP_TO_DATE = "up_to_date"
    SKIP = "skip"
    REPLACE = "replace"


@dataclass(frozen=True)
class FileOperation:
    strap_id: str
    kind: OperationKind
    source: Path
    target: Path
    force: bool = False


@dataclass(frozen=True)
class CronOperation:
    strap_id: str
    schedule: str
    command: str


@dataclass(frozen=True)
class StrapDefinition:
    identity: str
    path: Path
    name: str
    category: str
    file_operations: tuple[FileOperation, ...]
    cron_operations: tuple[CronOperation, ...]
    description: str = ""


@dataclass(frozen=True)
class TargetSnapshot:
    kind: str
    digest: str | None


@dataclass(frozen=True)
class PlannedAction:
    operation: FileOperation
    state: TargetState
    source_snapshot: TargetSnapshot
    target_snapshot: TargetSnapshot
    detail_targets: tuple[Path, ...] = ()


@dataclass(frozen=True)
class StrapPlan:
    strap: StrapDefinition
    actions: tuple[PlannedAction, ...]
    cron_entries: tuple[str, ...]


@dataclass(frozen=True)
class DeploymentPlan:
    home: Path
    straps: tuple[StrapPlan, ...]
    actions: tuple[PlannedAction, ...]
    cron_by_strap: tuple[tuple[str, tuple[str, ...]], ...]
    reconcile_all_cron: bool


@dataclass(frozen=True)
class ExecutionResult:
    completed: tuple[PlannedAction, ...]
    up_to_date: tuple[PlannedAction, ...]
    skipped: tuple[PlannedAction, ...]
