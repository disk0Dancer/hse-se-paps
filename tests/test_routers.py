from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_healthcheck():
    response = client.get("/")
    assert response.status_code == 200


def test_create_user():
    payload = {"login": "testuser", "password": "secret"}
    response = client.post("/user/", json=payload)
    assert response.status_code == 200
    user = response.json()
    assert user["login"] == "testuser"


def test_create_user_invalid():
    payload = {"login": "", "password": "secret"}
    response = client.post("/user/", json=payload)
    assert response.status_code == 422


def test_read_users():
    response = client.get("/user/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_read_users_not_found():
    response = client.get("/user/999999")
    assert response.status_code == 404


def test_update_user():
    # Create a user first
    payload = {"login": "updatable", "password": "pwd"}
    create_resp = client.post("/user/", json=payload)
    user_id = create_resp.json()["guid"]

    # Update user
    update_payload = {"password": "newpwd"}
    update_resp = client.put(f"/user/{user_id}", json=update_payload)
    assert update_resp.status_code == 200
    assert update_resp.json()["password"] == "newpwd"


def test_update_user_not_found():
    update_payload = {"password": "newpwd"}
    update_resp = client.put("/user/999999", json=update_payload)
    assert update_resp.status_code == 404


def test_delete_user():
    # Create a user first
    payload = {"login": "deletable", "password": "pwd"}
    create_resp = client.post("/user/", json=payload)
    user_id = create_resp.json()["guid"]

    # Delete user
    delete_resp = client.delete(f"/user/{user_id}")
    assert delete_resp.status_code == 200
    get_resp = client.get(f"/user/{user_id}")
    assert get_resp.status_code == 404


def test_delete_user_not_found():
    delete_resp = client.delete("/user/999999")
    assert delete_resp.status_code == 404


def test_search_user_positive():
    # create user first
    payload = {"login": "searchable", "password": "test123"}
    client.post("/user/", json=payload)
    # search
    resp = client.get("/user/search?login=search")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) > 0


def test_search_user_empty():
    resp = client.get("/user/search")
    assert resp.status_code == 200
    assert resp.json() == []
