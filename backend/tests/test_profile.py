from tests.conftest import auth_header, login, register


def test_user_can_get_own_profile(client, user_token):
    resp = client.get("/api/auth/me", headers=auth_header(user_token))
    assert resp.status_code == 200
    assert resp.get_json()["data"]["user"]["email"] == "user@test.com"


def test_sales_person_can_get_own_profile(client, sales_token):
    resp = client.get("/api/auth/me", headers=auth_header(sales_token))
    assert resp.status_code == 200
    assert resp.get_json()["data"]["user"]["role"] == "SALES_PERSON"


def test_user_can_update_own_profile(client, user_token):
    resp = client.put(
        "/api/auth/me",
        json={"name": "Updated Name", "phone": "9999999999", "address": "221B Baker Street"},
        headers=auth_header(user_token),
    )
    assert resp.status_code == 200
    user = resp.get_json()["data"]["user"]
    assert user["name"] == "Updated Name"
    assert user["phone"] == "9999999999"
    assert user["address"] == "221B Baker Street"

    fetched = client.get("/api/auth/me", headers=auth_header(user_token)).get_json()["data"]["user"]
    assert fetched["name"] == "Updated Name"


def test_sales_person_can_update_own_profile(client, sales_token):
    resp = client.put(
        "/api/auth/me",
        json={"name": "Seller Updated", "phone": "8888888888"},
        headers=auth_header(sales_token),
    )
    assert resp.status_code == 200
    user = resp.get_json()["data"]["user"]
    assert user["name"] == "Seller Updated"
    assert user["phone"] == "8888888888"


def test_user_cannot_update_another_users_profile(client, user_token):
    register(client, "Victim", "victim@test.com", "Password1")
    victim = login(client, "victim@test.com", "Password1").get_json()["data"]["user"]

    resp = client.put(
        "/api/auth/me",
        json={"name": "Hijacked", "user_id": victim["id"]},
        headers=auth_header(user_token),
    )
    assert resp.status_code == 200
    updated_user = resp.get_json()["data"]["user"]
    # The update always targets the authenticated caller, never the id in the body.
    assert updated_user["email"] == "user@test.com"

    victim_check = client.get("/api/auth/me", headers=auth_header(login(client, "victim@test.com", "Password1").get_json()["data"]["token"]))
    assert victim_check.get_json()["data"]["user"]["name"] == "Victim"


def test_sales_person_cannot_update_another_sales_persons_profile(client, sales_token, sales_token_2):
    resp = client.put(
        "/api/auth/me",
        json={"name": "Seller One Edited"},
        headers=auth_header(sales_token),
    )
    assert resp.status_code == 200

    seller_two = client.get("/api/auth/me", headers=auth_header(sales_token_2)).get_json()["data"]["user"]
    assert seller_two["name"] == "Seller Two"


def test_user_cannot_change_role_through_profile_update(client, user_token):
    resp = client.put(
        "/api/auth/me",
        json={"name": "Still A User", "role": "ADMIN"},
        headers=auth_header(user_token),
    )
    assert resp.status_code == 200
    assert resp.get_json()["data"]["user"]["role"] == "USER"


def test_sales_person_cannot_change_role_through_profile_update(client, sales_token):
    resp = client.put(
        "/api/auth/me",
        json={"name": "Still A Seller", "role": "ADMIN"},
        headers=auth_header(sales_token),
    )
    assert resp.status_code == 200
    assert resp.get_json()["data"]["user"]["role"] == "SALES_PERSON"


def test_profile_response_never_contains_password_hash(client, user_token):
    get_resp = client.get("/api/auth/me", headers=auth_header(user_token))
    assert "password_hash" not in get_resp.get_json()["data"]["user"]

    put_resp = client.put("/api/auth/me", json={"name": "No Hash Here"}, headers=auth_header(user_token))
    assert "password_hash" not in put_resp.get_json()["data"]["user"]


def test_unauthenticated_profile_request_rejected(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401

    put_resp = client.put("/api/auth/me", json={"name": "No Auth"})
    assert put_resp.status_code == 401


def test_profile_update_rejects_invalid_name(client, user_token):
    resp = client.put("/api/auth/me", json={"name": "a"}, headers=auth_header(user_token))
    assert resp.status_code == 400


def test_profile_update_cannot_change_password_hash(client, user_token):
    resp = client.put(
        "/api/auth/me",
        json={"name": "Safe Update", "password_hash": "hacked"},
        headers=auth_header(user_token),
    )
    assert resp.status_code == 200

    # The original password must still work — password_hash was never touched.
    login_resp = login(client, "user@test.com", "User@1234")
    assert login_resp.status_code == 200
