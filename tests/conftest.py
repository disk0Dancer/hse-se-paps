import os
import pytest


@pytest.fixture(
    scope="session",
    autouse=True,
)
def mock_env():
    os.environ["LLM_URL"] = "http://mock-llm-url.com"
    os.environ["LLM_CHAT_URL"] = "http://mock-llm-chat-url.com"
    os.environ["POSTGRES_CONN_URL"] = "postgresql://user:password@localhost/dbname"
