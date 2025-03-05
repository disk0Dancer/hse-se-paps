from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def get_auth_token(client, username, password):
    response = client.post(
        "/token",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return response.json()["access_token"]


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_create_user():
    token = get_auth_token(client, "admin", "adminpassword")
    response = client.post(
        "/user/",
        json={"login": "testuser", "password": "testpassword"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["login"] == "testuser"


def test_read_users():
    token = get_auth_token(client, "admin", "adminpassword")
    response = client.get("/user/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_update_user():
    token = get_auth_token(client, "admin", "adminpassword")
    response = client.put(
        "/user/1",
        json={"login": "updateduser", "password": "updatedpassword"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["login"] == "updateduser"


def test_delete_user():
    token = get_auth_token(client, "admin", "adminpassword")
    response = client.delete("/user/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_read_users_not_found():
    token = get_auth_token(client, "admin", "adminpassword")
    response = client.get("/user/999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404


def test_update_user_not_found():
    token = get_auth_token(client, "admin", "adminpassword")
    response = client.put(
        "/user/999",
        json={"login": "updateduser", "password": "updatedpassword"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


def test_delete_user_not_found():
    token = get_auth_token(client, "admin", "adminpassword")
    response = client.delete("/user/999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
