"""Package export management across different operating systems."""

import os
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Protocol


class PackageExporter(Protocol):
    """Protocol for OS-specific package exporters."""

    @property
    def os_name(self) -> str:
        """Name of the OS / distro identifier used for the output filename (e.g. 'arch')."""
        ...

    def is_available(self) -> bool:
        """Check if this exporter is applicable to the current system."""
        ...

    def export_packages(self) -> list[str]:
        """Export sorted list of explicitly installed package names."""
        ...


def get_linux_distro_id() -> str:
    """Detect Linux distribution ID from /etc/os-release or platform."""
    try:
        if hasattr(platform, "freedesktop_os_release"):
            data = platform.freedesktop_os_release()
            return data.get("ID", "").lower()
    except Exception:
        pass

    os_release = Path("/etc/os-release")
    if os_release.exists():
        try:
            for line in os_release.read_text(encoding="utf-8").splitlines():
                if line.startswith("ID="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'").lower()
        except Exception:
            pass

    return ""


class ArchPackageExporter:
    """Package exporter for Arch Linux and Arch-based distributions."""

    @property
    def os_name(self) -> str:
        return "arch"

    def is_available(self) -> bool:
        if shutil.which("pacman") is None:
            return False
        distro = get_linux_distro_id()
        if distro in {"arch", "manjaro", "endeavouros", "garuda", "cachyos", "artix"}:
            return True
        return platform.system() == "Linux" and shutil.which("pacman") is not None

    def export_packages(self) -> list[str]:
        result = subprocess.run(
            ["pacman", "-Qqe"],
            capture_output=True,
            text=True,
            check=True,
        )
        packages = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        return sorted(set(packages))


class FedoraPackageExporter:
    """Package exporter for Fedora and RPM-based distributions."""

    @property
    def os_name(self) -> str:
        return "fedora"

    def is_available(self) -> bool:
        if shutil.which("dnf") is None:
            return False
        distro = get_linux_distro_id()
        return distro in {"fedora", "rhel", "centos", "nobara", "rocky", "almalinux"}

    def export_packages(self) -> list[str]:
        result = subprocess.run(
            ["dnf", "repoquery", "--userinstalled", "--qf", "%{name}"],
            capture_output=True,
            text=True,
            check=True,
        )
        packages = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        return sorted(set(packages))


class DebianPackageExporter:
    """Package exporter for Debian, Ubuntu and derivatives."""

    @property
    def os_name(self) -> str:
        distro = get_linux_distro_id()
        return distro if distro in {"ubuntu", "debian"} else "debian"

    def is_available(self) -> bool:
        if shutil.which("apt-mark") is None:
            return False
        distro = get_linux_distro_id()
        return distro in {"debian", "ubuntu", "pop", "mint", "elementary"}

    def export_packages(self) -> list[str]:
        result = subprocess.run(
            ["apt-mark", "showmanual"],
            capture_output=True,
            text=True,
            check=True,
        )
        packages = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        return sorted(set(packages))


class DarwinPackageExporter:
    """Package exporter for macOS using Homebrew."""

    @property
    def os_name(self) -> str:
        return "darwin"

    def is_available(self) -> bool:
        return platform.system() == "Darwin" and shutil.which("brew") is not None

    def export_packages(self) -> list[str]:
        result = subprocess.run(
            ["brew", "leaves"],
            capture_output=True,
            text=True,
            check=True,
        )
        packages = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        return sorted(set(packages))


DEFAULT_EXPORTERS: list[PackageExporter] = [
    ArchPackageExporter(),
    FedoraPackageExporter(),
    DebianPackageExporter(),
    DarwinPackageExporter(),
]


def get_current_exporter(
    exporters: list[PackageExporter] | None = None,
) -> PackageExporter | None:
    """Find the first matching exporter for the current operating system."""
    candidates = exporters if exporters is not None else DEFAULT_EXPORTERS
    for exporter in candidates:
        if exporter.is_available():
            return exporter
    return None


def sync_packages(
    repo_root: Path,
    exporter: PackageExporter | None = None,
) -> Path | None:
    """
    Export installed packages for the current OS into vendored/packages/<os_name>.txt.

    Args:
        repo_root: Path to the dotfiles repository root.
        exporter: Optional custom exporter to use (auto-detected if None).

    Returns:
        Path to the written package file if successful, or None if skipped/unsupported.
    """
    active_exporter = exporter or get_current_exporter()
    if active_exporter is None:
        return None

    packages = active_exporter.export_packages()
    if not packages:
        return None

    target_dir = repo_root / "vendored" / "packages"
    target_dir.mkdir(parents=True, exist_ok=True)

    target_file = target_dir / f"{active_exporter.os_name}.txt"
    content = "\n".join(packages) + "\n"

    # Only write if content changed or file doesn't exist
    if target_file.exists():
        try:
            existing = target_file.read_text(encoding="utf-8")
            if existing == content:
                return target_file
        except Exception:
            pass

    target_file.write_text(content, encoding="utf-8")
    return target_file
