"""Smoke test: the package installs, imports, and its CLI entry point runs."""

from importlib.metadata import version

import pincitecheck


def test_package_is_installed_with_a_version():
    # Checks the package is installed, not a specific number, so version bumps don't break it
    assert version("pincitecheck")


def test_main_runs(capsys):
    pincitecheck.main()
    captured = capsys.readouterr()
    assert "pincitecheck" in captured.out
