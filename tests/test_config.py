"""Tests for pincitecheck.config.

These never read the real .env: every test passes _env_file explicitly and controls the
environment with monkeypatch, so they behave the same locally and in CI (which has no token).
"""

import pytest
from pydantic import ValidationError

from pincitecheck.config import Settings

TOKEN_VAR = "COURTLISTENER_API_TOKEN"
FAKE_TOKEN = "fake-token-for-tests"


@pytest.fixture(autouse=True)
def clear_token_env(monkeypatch):
    """Start every test with the token unset, even if the developer's shell exports it."""
    monkeypatch.delenv(TOKEN_VAR, raising=False)


def test_loads_token_from_environment(monkeypatch):
    monkeypatch.setenv(TOKEN_VAR, FAKE_TOKEN)

    settings = Settings(_env_file=None)

    assert settings.courtlistener_api_token.get_secret_value() == FAKE_TOKEN


def test_token_is_masked_in_repr(monkeypatch):
    monkeypatch.setenv(TOKEN_VAR, FAKE_TOKEN)

    settings = Settings(_env_file=None)

    assert FAKE_TOKEN not in repr(settings)
    assert FAKE_TOKEN not in str(settings)


def test_missing_token_raises():
    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_empty_token_raises(monkeypatch):
    # The unfilled placeholder copied from .env.example.
    monkeypatch.setenv(TOKEN_VAR, "")

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_loads_token_from_env_file(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(f"{TOKEN_VAR}={FAKE_TOKEN}\n")

    settings = Settings(_env_file=env_file)

    assert settings.courtlistener_api_token.get_secret_value() == FAKE_TOKEN


def test_environment_overrides_env_file(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text(f"{TOKEN_VAR}=token-from-file\n")
    monkeypatch.setenv(TOKEN_VAR, "token-from-environment")

    settings = Settings(_env_file=env_file)

    assert settings.courtlistener_api_token.get_secret_value() == "token-from-environment"
