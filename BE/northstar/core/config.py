from functools import lru_cache
from typing import Annotated

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    app_name: str = "Northstar API"
    app_env: str = "local"
    app_debug: bool = False
    app_key: str = Field(min_length=32)
    database_url: str = "sqlite:////data/database.sqlite"
    frontend_origins: Annotated[list[str], NoDecode] = ["http://localhost:5173"]
    trusted_hosts: Annotated[list[str], NoDecode] = ["localhost", "127.0.0.1", "testserver"]
    session_cookie: str = "northstar_session"
    session_lifetime_minutes: int = 60
    cookie_secure: bool = False
    api_rate_limit: int = 240
    login_rate_limit: int = 8
    max_request_bytes: int = Field(default=1_048_576, ge=16_384, le=10_485_760)
    session_touch_interval_seconds: int = Field(default=300, ge=60, le=3600)
    enable_hsts: bool = False
    hsts_max_age: int = Field(default=31_536_000, ge=300)
    content_security_policy: str = (
        "default-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'"
    )

    @field_validator("frontend_origins", "trusted_hosts", mode="before")
    @classmethod
    def split_csv(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        if self.app_env.lower() != "production":
            return self
        if self.app_debug:
            raise ValueError("APP_DEBUG must be false in production.")
        if not self.cookie_secure:
            raise ValueError("COOKIE_SECURE must be true in production.")
        if not self.enable_hsts:
            raise ValueError("ENABLE_HSTS must be true in production.")
        if not self.session_cookie.startswith("__Host-"):
            raise ValueError("Production SESSION_COOKIE must use the __Host- prefix.")
        if any(not origin.startswith("https://") for origin in self.frontend_origins):
            raise ValueError("Every production frontend origin must use HTTPS.")
        if any(host in {"localhost", "127.0.0.1", "testserver"} for host in self.trusted_hosts):
            raise ValueError("Local hosts are not allowed in production.")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
