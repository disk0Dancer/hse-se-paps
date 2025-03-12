import os

os.environ["LLM_URL"] = "http://mock-llm-url.com"
os.environ["LLM_CHAT_URL"] = "http://mock-llm-chat-url.com"
os.environ["POSTGRES_CONN_URL"] = "postgresql+asyncpg://user:password@localhost/dbname"

from src.services.auth import AuthService


def test_create_token(mock_user):
    user = mock_user
    token = AuthService.create_token(user)
    assert token is not None
    assert token.access_token is not None
    assert token.refresh_token is not None


def test_verify_token(mock_user):
    user = mock_user
    token = AuthService.create_token(user)
    payload = AuthService.verify_token(token.access_token)
    assert payload is not None
    assert payload["sub"] == user.login


def test_token_expiration(mock_user):
    user = mock_user
    token = AuthService.create_token(user)
    assert token.expires_at is not None
    verified_payload = AuthService.verify_token(token.access_token)
    assert verified_payload["exp"] is not None
