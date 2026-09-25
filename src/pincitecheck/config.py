"""Runtime configuration, loaded from environment variables and a local .env file.

Real environment variables take precedence over .env, so the same code works locally
(.env), in Docker (-e / --env-file), and on AWS (Secrets Manager injected as env vars).
"""

from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        # Other tools may put their own variables in .env; don't fail on them.
        extra="ignore",
    )

    # Read from COURTLISTENER_API_TOKEN. SecretStr masks the value in repr, logs, and
    # tracebacks; call .get_secret_value() only where the HTTP header is built.
    # min_length=1 rejects the empty placeholder copied from .env.example.
    courtlistener_api_token: SecretStr = Field(min_length=1)


@lru_cache
def get_settings() -> Settings:
    """Load settings once and reuse them. Raises ValidationError if the token is missing."""
    return Settings()
