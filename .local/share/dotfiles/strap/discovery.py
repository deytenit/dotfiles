"""Discover and validate declarative strap documents."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from dotfiles.vendor import yaml_parser

from .models import CronOperation, FileOperation, OperationKind, StrapDefinition


ACCEPTED_NAME = re.compile(r"^(?:([A-Za-z0-9][A-Za-z0-9_-]*)\.)?strap\.yaml$")
LEGACY_NAME = re.compile(r"^(?:strap@.+|.+\.strap@.+)\.yaml$")
PLATFORMS = {"generic", "linux", "darwin"}
OPERATIONS = {"link", "copy", "cron"}


class StrapValidationError(RuntimeError):
    def __init__(self, errors: tuple[str, ...]):
        self.errors = errors
        super().__init__("\n".join(errors))


def discover_straps(
    repo_root: Path, *, home: Path, platform_name: str
) -> tuple[StrapDefinition, ...]:
    root = repo_root.absolute()
    home = home.absolute()
    errors: list[str] = []
    definitions: list[StrapDefinition] = []
    for path in _strap_paths(root):
        relative = path.relative_to(root).as_posix()
        if path.name == ".strap" or LEGACY_NAME.fullmatch(path.name):
            errors.append(f"{relative}: legacy strap filename is not supported")
            continue
        if not ACCEPTED_NAME.fullmatch(path.name):
            continue
        try:
            definition = _parse_definition(path, root, home, platform_name)
        except _DocumentError as error:
            errors.extend(f"{relative}: {message}" for message in error.errors)
        else:
            if definition.file_operations or definition.cron_operations:
                definitions.append(definition)
    if errors:
        raise StrapValidationError(tuple(errors))
    return tuple(sorted(definitions, key=lambda item: (item.category, item.name, item.identity)))


def _strap_paths(root: Path) -> list[Path]:
    found: list[Path] = []
    resolved_root = root.resolve()
    for current, directories, files in os.walk(root, followlinks=False):
        current_path = Path(current)
        directories[:] = [
            directory for directory in directories
            if directory not in {".git", "__pycache__"}
            and _is_beneath((current_path / directory).resolve(), resolved_root)
        ]
        found.extend(current_path / filename for filename in files)
    return sorted(found)


def _parse_definition(path: Path, root: Path, home: Path, platform_name: str) -> StrapDefinition:
    try:
        document = yaml_parser.safe_load(path.read_text())
    except (OSError, yaml_parser.YAMLParseError) as error:
        raise _DocumentError((f"cannot parse YAML: {error}",)) from error
    if not isinstance(document, dict):
        raise _DocumentError(("document must be a mapping",))
    errors: list[str] = []
    name = _required_string(document, "name", errors)
    category = _required_string(document, "category", errors)
    description = _required_string(document, "description", errors)
    platforms = document.get("platforms")
    if not isinstance(platforms, dict):
        errors.append("platforms must be a mapping")
        platforms = {}
    else:
        errors.extend(f"unknown platform {key!r}" for key in platforms if key not in PLATFORMS)
    identity = path.relative_to(root).as_posix()
    files: list[FileOperation] = []
    cron: list[CronOperation] = []
    for platform in ("generic", platform_name) if platform_name in {"linux", "darwin"} else ("generic",):
        block = platforms.get(platform)
        if block is None:
            continue
        if not isinstance(block, dict):
            errors.append(f"platforms.{platform} must be a mapping")
            continue
        errors.extend(
            f"platforms.{platform}: unknown operation {key!r}"
            for key in block if key not in OPERATIONS
        )
        files.extend(_file_operations(block.get("link"), OperationKind.LINK, path.parent, root, home, identity, errors))
        files.extend(_file_operations(block.get("copy"), OperationKind.COPY, path.parent, root, home, identity, errors))
        cron.extend(_cron_operations(block.get("cron"), home, identity, errors))
    if errors:
        raise _DocumentError(tuple(errors))
    return StrapDefinition(identity, path, name, category, tuple(files), tuple(cron), description)


def _required_string(document: dict[str, Any], key: str, errors: list[str]) -> str:
    value = document.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{key} must be a non-empty string")
        return ""
    return value


def _file_operations(
    entries: Any, kind: OperationKind, strap_dir: Path, repo_root: Path, home: Path, identity: str, errors: list[str]
) -> list[FileOperation]:
    if entries is None:
        return []
    if not isinstance(entries, list):
        errors.append(f"{kind.value} must be a list")
        return []
    operations: list[FileOperation] = []
    for index, entry in enumerate(entries):
        label = f"{kind.value}[{index}]"
        force = False
        if isinstance(entry, str):
            source_text, target_text = entry, None
        elif isinstance(entry, list) and len(entry) == 2 and all(isinstance(item, str) for item in entry):
            source_text, target_text = entry
        elif kind is OperationKind.COPY and isinstance(entry, dict):
            unknown = set(entry) - {"source", "target", "force"}
            if unknown:
                errors.append(f"{label} has unknown keys: {', '.join(sorted(unknown))}")
                continue
            source_text, target_text = entry.get("source"), entry.get("target")
            force = entry.get("force", False)
            if not isinstance(force, bool):
                errors.append(f"{label}.force must be boolean")
                continue
        else:
            errors.append(f"{label} must be a source string, [source, target], or copy object")
            continue
        if not isinstance(source_text, str) or not source_text:
            errors.append(f"{label}.source must be a non-empty string")
            continue
        if target_text is not None and (not isinstance(target_text, str) or not target_text):
            errors.append(f"{label}.target must be a non-empty string")
            continue
        source = (strap_dir / source_text).absolute()
        if target_text is None:
            target = home / strap_dir.relative_to(repo_root) / source_text
        else:
            target = _target(home, target_text)
        operations.append(FileOperation(identity, kind, source, target, force))
    return operations


def _target(home: Path, value: str) -> Path:
    if value == "~":
        return home
    if value.startswith("~/"):
        return home / value[2:]
    return home / value


def _cron_operations(entries: Any, home: Path, identity: str, errors: list[str]) -> list[CronOperation]:
    if entries is None:
        return []
    if not isinstance(entries, list):
        errors.append("cron must be a list")
        return []
    result: list[CronOperation] = []
    for index, entry in enumerate(entries):
        if not (isinstance(entry, list) and len(entry) == 2 and all(isinstance(value, str) for value in entry)):
            errors.append(f"cron[{index}] must be [schedule, command]")
            continue
        schedule, command = entry
        if not _valid_schedule(schedule):
            errors.append(f"cron[{index}] has an invalid schedule")
        if not command.strip():
            errors.append(f"cron[{index}] command must not be empty")
        if _valid_schedule(schedule) and command.strip():
            command = str(_target(home, command)) if command == "~" or command.startswith("~/") else command
            result.append(CronOperation(identity, schedule, command))
    return result


def _valid_schedule(schedule: str) -> bool:
    fields = schedule.split()
    if len(fields) != 5:
        return False
    return all(_valid_field(field, low, high) for field, low, high in zip(fields, (0, 0, 1, 1, 0), (59, 23, 31, 12, 7)))


def _valid_field(field: str, low: int, high: int) -> bool:
    for part in field.split(","):
        base, *step = part.split("/")
        if len(step) > 1 or (step and (not step[0].isdigit() or int(step[0]) <= 0)):
            return False
        if base == "*":
            continue
        match = re.fullmatch(r"(\d+)(?:-(\d+))?", base)
        if not match:
            return False
        start, end = int(match.group(1)), int(match.group(2) or match.group(1))
        if start < low or end > high or start > end:
            return False
    return True


def _is_beneath(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


class _DocumentError(Exception):
    def __init__(self, errors: tuple[str, ...]):
        self.errors = errors
