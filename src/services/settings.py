from typing import Any

from pydantic import (
    BaseModel,
    Field,
    PostgresDsn,
)

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    llm_url: str = Field()  # TODO: add loading env
    llm_chat_url: str = Field()

    sqlite_url: str = "sqlite:///./test.db"

    pg_dsn: PostgresDsn = "postgres://user:pass@localhost:5432/foobar"
    model_config = SettingsConfigDict(env_prefix="my_prefix_")

    _env_file = ".env"


settings = Settings(llm_url="", llm_chat_url="").model_dump()
