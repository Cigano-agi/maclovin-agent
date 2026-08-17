import pytest
import subprocess
import sys


def test_cli_check_command():
    result = subprocess.run(
        [sys.executable, "-m", "maclovin", "check"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert result.returncode == 0
    assert "Diagnosticando ambiente do maclovin" in result.stdout
    assert "SQLite" in result.stdout


def test_cli_dry_run():
    result = subprocess.run(
        [sys.executable, "-m", "maclovin", "run", "--dry-run"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert result.returncode == 0
    assert "MACLOVIN" in result.stdout


def test_cli_status_command():
    result = subprocess.run(
        [sys.executable, "-m", "maclovin", "status"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert result.returncode == 0
