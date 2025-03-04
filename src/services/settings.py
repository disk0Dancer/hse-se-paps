import os

class Settings:
    llm_url: str = os.getenv("LLM_URL", None)
    llm_chat_url: str = os.getenv("LLM_CHAT_URL", None)
    pg_dsn: str = os.getenv("POSTGRES_CONN_URL", None)
    
    def __init__(self):
        if not self.llm_url:
            raise ValueError("LLM_URL is not set")
        if not self.llm_chat_url:
            raise ValueError("LLM_CHAT_URL is not set")
        if not self.pg_dsn:
            raise ValueError("POSTGRES_CONN_URL is not set")
        
settings = Settings()
