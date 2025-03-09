import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    def __init__(self):
        self.llm_url: str = os.getenv("LLM_URL", None)
        self.llm_chat_url: str = os.getenv("LLM_CHAT_URL", None)
        self.pg_dsn: str = os.getenv("POSTGRES_CONN_URL", None)
        # JWT settings
        self.secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")
        self.access_token_expire_minutes: int = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
        )

        if not self.llm_url:
            raise ValueError("LLM_URL is not set")
        if not self.llm_chat_url:
            raise ValueError("LLM_CHAT_URL is not set")
        if not self.pg_dsn:
            raise ValueError("POSTGRES_CONN_URL is not set")
        if self.access_token_expire_minutes <= 0:
            raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES must be greater than 0")


settings = Settings()
