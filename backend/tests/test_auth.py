from tests.conftest import auth_header, login, register


def test_register_user_success(client):
    resp = register(client, "Jane Doe", "jane@test.com", "Password1")
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["success"] is True
    assert body["data"]["user"]["role"] == "USER"
    assert "password_hash" not in body["data"]["user"]
    assert body["data"]["token"]


def test_register_duplicate_email_rejected(client):
    register(client, "Jane Doe", "dupe@test.com", "Password1")
    resp = register(client, "Jane Two", "dupe@test.com", "Password1")
    assert resp.status_code == 409


def test_register_weak_password_rejected(client):
    resp = register(client, "Jane Doe", "weak@test.com", "abc")
    assert resp.status_code == 400


def test_login_success(client):
    register(client, "Jane Doe", "login@test.com", "Password1")
    resp = login(client, "login@test.com", "Password1")
    assert resp.status_code == 200
    assert resp.get_json()["data"]["token"]


def test_login_wrong_password(client):
    register(client, "Jane Doe", "wrongpw@test.com", "Password1")
    resp = login(client, "wrongpw@test.com", "WrongPass1")
    assert resp.status_code == 401


def test_login_admin(client, admin_token):
    resp = client.get("/api/auth/me", headers=auth_header(admin_token))
    assert resp.status_code == 200
    assert resp.get_json()["data"]["user"]["role"] == "ADMIN"


def test_login_sales_person(client, sales_token):
    resp = client.get("/api/auth/me", headers=auth_header(sales_token))
    assert resp.status_code == 200
    assert resp.get_json()["data"]["user"]["role"] == "SALES_PERSON"


def test_missing_token_rejected(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_invalid_token_rejected(client):
    resp = client.get("/api/auth/me", headers=auth_header("not-a-real-token"))
    assert resp.status_code == 401
