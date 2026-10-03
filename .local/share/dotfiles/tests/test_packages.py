"""Tests for the package export system."""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from packages.exporter import (
    ArchPackageExporter,
    DarwinPackageExporter,
    DebianPackageExporter,
    FedoraPackageExporter,
    get_current_exporter,
    sync_packages,
)


class ArchPackageExporterTest(unittest.TestCase):
    @patch("packages.exporter.shutil.which")
    @patch("packages.exporter.get_linux_distro_id")
    def test_availability(self, get_distro, which):
        which.return_value = "/usr/bin/pacman"
        get_distro.return_value = "arch"
        exporter = ArchPackageExporter()
        self.assertTrue(exporter.is_available())

        which.return_value = None
        self.assertFalse(exporter.is_available())

    @patch("packages.exporter.subprocess.run")
    def test_export_packages(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="zsh\nbash\n7zip\n",
            returncode=0,
        )
        exporter = ArchPackageExporter()
        packages = exporter.export_packages()
        self.assertEqual(packages, ["7zip", "bash", "zsh"])
        mock_run.assert_called_once_with(
            ["pacman", "-Qqe"],
            capture_output=True,
            text=True,
            check=True,
        )


class FedoraPackageExporterTest(unittest.TestCase):
    @patch("packages.exporter.shutil.which")
    @patch("packages.exporter.get_linux_distro_id")
    def test_availability(self, get_distro, which):
        which.return_value = "/usr/bin/dnf"
        get_distro.return_value = "fedora"
        exporter = FedoraPackageExporter()
        self.assertTrue(exporter.is_available())

        get_distro.return_value = "arch"
        self.assertFalse(exporter.is_available())

    @patch("packages.exporter.subprocess.run")
    def test_export_packages(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="ripgrep\ncurl\n",
            returncode=0,
        )
        exporter = FedoraPackageExporter()
        packages = exporter.export_packages()
        self.assertEqual(packages, ["curl", "ripgrep"])


class SyncPackagesTest(unittest.TestCase):
    def test_sync_packages_writes_to_vendored_packages(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            mock_exporter = MagicMock()
            mock_exporter.os_name = "testos"
            mock_exporter.export_packages.return_value = ["pkg-b", "pkg-a"]

            target = sync_packages(repo_root, exporter=mock_exporter)
            self.assertIsNotNone(target)
            self.assertTrue(target.exists())
            self.assertEqual(target.parent, repo_root / "vendored" / "packages")
            self.assertEqual(target.name, "testos.txt")
            self.assertEqual(target.read_text(encoding="utf-8"), "pkg-b\npkg-a\n")

    def test_sync_packages_skips_write_if_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            target_dir = repo_root / "vendored" / "packages"
            target_dir.mkdir(parents=True)
            file_path = target_dir / "testos.txt"
            file_path.write_text("pkg-a\n", encoding="utf-8")
            mtime_before = file_path.stat().st_mtime_ns

            mock_exporter = MagicMock()
            mock_exporter.os_name = "testos"
            mock_exporter.export_packages.return_value = ["pkg-a"]

            target = sync_packages(repo_root, exporter=mock_exporter)
            self.assertEqual(target, file_path)
            self.assertEqual(file_path.stat().st_mtime_ns, mtime_before)


if __name__ == "__main__":
    unittest.main()
