"""Per-strap crontab section rendering and installation."""

from __future__ import annotations

import hashlib
import subprocess
import tempfile
from pathlib import Path
from typing import Mapping, Protocol


PREFIX = "DEYTENIT DOTFILES STRAP CRON"
LEGACY_BEGIN = f"# BEGIN {PREFIX}"
LEGACY_END = f"# END {PREFIX}"


class CronError(RuntimeError):
    pass


class CrontabBackend(Protocol):
    def read(self) -> str: ...
    def install(self, content: str) -> None: ...


def section_key(strap_id: str) -> str:
    return hashlib.sha256(strap_id.encode("utf-8")).hexdigest()


def begin_marker(strap_id: str) -> str:
    return f"# BEGIN {PREFIX} {section_key(strap_id)} {strap_id}"


def end_marker(strap_id: str) -> str:
    return f"# END {PREFIX} {section_key(strap_id)}"


def render_crontab(current: str, desired: Mapping[str, tuple[str, ...]], *, reconcile_all: bool) -> str:
    lines = current.splitlines()
    sections, consumed = _sections(lines)
    kept = [line for index, line in enumerate(lines) if index not in consumed]
    if not reconcile_all:
        selected = set(desired)
        kept = [line for index, line in enumerate(lines) if index not in consumed or not _inside(index, sections, selected)]
    _legacy_valid(lines)
    if reconcile_all:
        kept = _remove_legacy(kept)
    rendered = list(kept)
    for strap_id in sorted(desired):
        entries = desired[strap_id]
        if entries:
            if rendered and rendered[-1]:
                rendered.append("")
            rendered.extend((begin_marker(strap_id), *entries, end_marker(strap_id)))
    return "\n".join(rendered).rstrip("\n") + "\n"


def _sections(lines: list[str]) -> tuple[dict[str, tuple[int, int]], set[int]]:
    sections, consumed, open_section = {}, set(), None
    for index, line in enumerate(lines):
        if line.startswith(f"# BEGIN {PREFIX} "):
            parts = line.removeprefix(f"# BEGIN {PREFIX} ").split(" ", 1)
            if len(parts) != 2 or open_section is not None:
                raise CronError("malformed or nested managed cron marker")
            key, strap_id = parts
            if key != section_key(strap_id) or strap_id in sections:
                raise CronError("invalid or duplicate managed cron marker")
            open_section = (strap_id, index)
        elif line.startswith(f"# END {PREFIX} "):
            key = line.removeprefix(f"# END {PREFIX} ")
            if not key or " " in key or open_section is None or key != section_key(open_section[0]):
                raise CronError("unmatched managed cron marker")
            strap_id, start = open_section
            sections[strap_id] = (start, index)
            consumed.update(range(start, index + 1))
            open_section = None
    if open_section is not None:
        raise CronError("unterminated managed cron marker")
    return sections, consumed


def _inside(index, sections, selected):
    return any(strap_id in selected and start <= index <= end for strap_id, (start, end) in sections.items())


def _legacy_valid(lines):
    begins = [i for i, line in enumerate(lines) if line == LEGACY_BEGIN]
    ends = [i for i, line in enumerate(lines) if line == LEGACY_END]
    if bool(begins) != bool(ends) or len(begins) > 1 or len(ends) > 1 or (begins and begins[0] > ends[0]):
        raise CronError("malformed legacy managed cron marker")


def _remove_legacy(lines):
    try:
        start, end = lines.index(LEGACY_BEGIN), lines.index(LEGACY_END)
    except ValueError:
        return lines
    return lines[:start] + lines[end + 1:]


def apply_cron_plan(plan, backend: CrontabBackend) -> None:
    original = backend.read()
    desired = dict(plan.cron_by_strap)
    try:
        backend.install(render_crontab(original, desired, reconcile_all=plan.reconcile_all_cron))
    except Exception as error:
        try:
            backend.install(original)
        except Exception as restore_error:
            raise CronError(f"cron installation failed ({error}); restoration failed ({restore_error})") from error
        raise CronError(f"cron installation failed; original crontab restored: {error}") from error


class SystemCrontab:
    def read(self) -> str:
        try:
            result = subprocess.run(["crontab", "-l"], text=True, capture_output=True, check=False)
        except OSError as error:
            raise CronError(f"cannot read crontab: {error}") from error
        if result.returncode == 0:
            return result.stdout
        if result.returncode == 1 and "no crontab" in result.stderr.lower():
            return ""
        raise CronError(result.stderr.strip() or "cannot read crontab")

    def install(self, content: str) -> None:
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as handle:
            handle.write(content)
            path = Path(handle.name)
        try:
            result = subprocess.run(["crontab", str(path)], text=True, capture_output=True, check=False)
            if result.returncode:
                raise CronError(result.stderr.strip() or "cannot install crontab")
        finally:
            path.unlink(missing_ok=True)
