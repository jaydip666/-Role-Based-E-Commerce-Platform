from tests.conftest import auth_header, login, register


def test_admin_can_view_users(client, admin_token):
    resp = client.get("/api/admin/users", headers=auth_header(admin_token))
    assert resp.status_code == 200
    assert resp.get_json()["data"]["count"] >= 1


def test_admin_can_change_user_role(client, admin_token, user_token):
    users = client.get("/api/admin/users", headers=auth_header(admin_token)).get_json()["data"]["users"]
    target = next(u for u in users if u["role"] == "USER")

    resp = client.put(
        f"/api/admin/users/{target['id']}/role",
        json={"role": "SALES_PERSON"},
        headers=auth_header(admin_token),
    )
    assert resp.status_code == 200
    assert resp.get_json()["data"]["user"]["role"] == "SALES_PERSON"


def test_admin_can_edit_safe_user_information(client, admin_token, user_token):
    users = client.get("/api/admin/users", headers=auth_header(admin_token)).get_json()["data"]["users"]
    target = next(u for u in users if u["role"] == "USER")

    resp = client.put(
        f"/api/admin/users/{target['id']}",
        json={"name": "Edited By Admin", "phone": "9999999999", "address": "Somewhere"},
        headers=auth_header(admin_token),
    )
    assert resp.status_code == 200
    updated = resp.get_json()["data"]["user"]
    assert updated["name"] == "Edited By Admin"
    assert updated["phone"] == "9999999999"
    assert updated["address"] == "Somewhere"
    assert updated["role"] == "USER"


def test_admin_edit_cannot_change_role_or_expose_password_hash(client, admin_token, user_token):
    users = client.get("/api/admin/users", headers=auth_header(admin_token)).get_json()["data"]["users"]
    target = next(u for u in users if u["role"] == "USER")

    resp = client.put(
        f"/api/admin/users/{target['id']}",
        json={"name": "Still Safe", "role": "ADMIN", "password_hash": "hacked"},
        headers=auth_header(admin_token),
    )
    assert resp.status_code == 200
    updated = resp.get_json()["data"]["user"]
    assert updated["role"] == "USER"
    assert "password_hash" not in updated


def test_admin_can_delete_a_user(client, admin_token, user_token):
    users = client.get("/api/admin/users", headers=auth_header(admin_token)).get_json()["data"]["users"]
    target = next(u for u in users if u["role"] == "USER")

    resp = client.delete(f"/api/admin/users/{target['id']}", headers=auth_header(admin_token))
    assert resp.status_code == 200

    remaining = client.get("/api/admin/users", headers=auth_header(admin_token)).get_json()["data"]["users"]
    assert all(u["id"] != target["id"] for u in remaining)


def test_admin_cannot_delete_own_account(client, admin_token):
    users = client.get("/api/admin/users", headers=auth_header(admin_token)).get_json()["data"]["users"]
    self_user = next(u for u in users if u["role"] == "ADMIN")

    resp = client.delete(f"/api/admin/users/{self_user['id']}", headers=auth_header(admin_token))
    assert resp.status_code == 400

    still_there = client.get("/api/admin/users", headers=auth_header(admin_token)).get_json()["data"]["users"]
    assert any(u["id"] == self_user["id"] for u in still_there)


def test_sales_person_cannot_manage_users(client, sales_token, user_token):
    users = client.get("/api/admin/users", headers=auth_header(sales_token))
    assert users.status_code == 403

    resp = client.put(
        f"/api/admin/users/000000000000000000000000",
        json={"name": "X"},
        headers=auth_header(sales_token),
    )
    assert resp.status_code == 403

    resp = client.delete("/api/admin/users/000000000000000000000000", headers=auth_header(sales_token))
    assert resp.status_code == 403


def test_user_cannot_manage_users(client, user_token):
    users = client.get("/api/admin/users", headers=auth_header(user_token))
    assert users.status_code == 403

    resp = client.put(
        f"/api/admin/users/000000000000000000000000",
        json={"name": "X"},
        headers=auth_header(user_token),
    )
    assert resp.status_code == 403

    resp = client.delete("/api/admin/users/000000000000000000000000", headers=auth_header(user_token))
    assert resp.status_code == 403


def test_non_admin_cannot_change_another_users_role(client, user_token):
    register(client, "Victim", "role-victim@test.com", "Password1")
    victim = login(client, "role-victim@test.com", "Password1").get_json()["data"]["user"]

    resp = client.put(
        f"/api/admin/users/{victim['id']}/role",
        json={"role": "ADMIN"},
        headers=auth_header(user_token),
    )
    assert resp.status_code == 403


def test_password_hash_never_returned_from_admin_endpoints(client, admin_token, user_token):
    users = client.get("/api/admin/users", headers=auth_header(admin_token)).get_json()["data"]["users"]
    assert all("password_hash" not in u for u in users)
    target = next(u for u in users if u["role"] == "USER")

    role_resp = client.put(
        f"/api/admin/users/{target['id']}/role",
        json={"role": "SALES_PERSON"},
        headers=auth_header(admin_token),
    )
    assert "password_hash" not in role_resp.get_json()["data"]["user"]

    edit_resp = client.put(
        f"/api/admin/users/{target['id']}",
        json={"name": "No Hash"},
        headers=auth_header(admin_token),
    )
    assert "password_hash" not in edit_resp.get_json()["data"]["user"]
