from src.services.auth import AuthService
from src.models.user import User


def test_create_token():
    user = User(email="test@example.com", login="testuser", password="password123")
    token = AuthService.create_token(user)
    assert token is not None
    assert token.access_token is not None
    assert token.refresh_token is not None


def test_verify_token():
    user = User(email="test@example.com", login="testuser", password="password123")
    token = AuthService.create_token(user)
    payload = AuthService.verify_token(token.access_token)
    assert payload is not None
    assert payload["sub"] == user.login


def test_token_expiration():
    user = User(email="test@example.com", login="testuser", password="password123")
    token = AuthService.create_token(user)
    assert token.expires_at is not None
    verified_payload = AuthService.verify_token(token.access_token)
    assert verified_payload["exp"] is not None
