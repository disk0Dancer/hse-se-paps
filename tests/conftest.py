import pytest


@pytest.fixture(
    scope="session",
    autouse=True,
)
def mock_user():
    class User:
        def __init__(self, email, login, password):
            self.email = email
            self.login = login
            self.password = password

    return User(email="test@example.com", login="testuser", password="password123")
