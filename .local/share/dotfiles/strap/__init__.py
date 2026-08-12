"""Public bootstrap API."""

from .models import (
    CronOperation,
    DeploymentPlan,
    ExecutionResult,
    FileOperation,
    OperationKind,
    PlannedAction,
    SetupMode,
    StrapDefinition,
    StrapPlan,
    TargetSnapshot,
    TargetState,
)


def run_bootstrap(*args, **kwargs):
    """Run the bootstrap application without eagerly importing its UI."""
    from .app import run_bootstrap as implementation

    return implementation(*args, **kwargs)


__all__ = [
    "CronOperation", "DeploymentPlan", "ExecutionResult", "FileOperation",
    "OperationKind", "PlannedAction", "SetupMode", "StrapDefinition", "StrapPlan",
    "TargetSnapshot", "TargetState", "run_bootstrap",
]
