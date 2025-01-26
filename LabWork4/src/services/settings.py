from typing import Any

from pydantic import (
    BaseModel,
    Field,
    ImportString,
    PostgresDsn,
)

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    llm_url: str = Field()
    llm_chat_url: str = Field()

    pg_dsn: PostgresDsn = "postgres://user:pass@localhost:5432/foobar"
    model_config = SettingsConfigDict(env_prefix="my_prefix_")

    _env_file = ".env"


settings = Settings().model_dump()
