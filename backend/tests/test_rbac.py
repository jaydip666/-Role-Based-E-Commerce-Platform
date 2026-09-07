from tests.conftest import auth_header


def test_user_cannot_access_admin_users_list(client, user_token):
    resp = client.get("/api/admin/users", headers=auth_header(user_token))
    assert resp.status_code == 403


def test_sales_person_cannot_access_admin_users_list(client, sales_token):
    resp = client.get("/api/admin/users", headers=auth_header(sales_token))
    assert resp.status_code == 403


def test_admin_can_access_admin_users_list(client, admin_token):
    resp = client.get("/api/admin/users", headers=auth_header(admin_token))
    assert resp.status_code == 200


def test_admin_can_change_user_role(client, admin_token, user_token):
    resp = client.get("/api/admin/users", headers=auth_header(admin_token))
    users = resp.get_json()["data"]["users"]
    target = next(u for u in users if u["role"] == "USER")

    update_resp = client.put(
        f"/api/admin/users/{target['id']}/role",
        json={"role": "SALES_PERSON"},
        headers=auth_header(admin_token),
    )
    assert update_resp.status_code == 200
    assert update_resp.get_json()["data"]["user"]["role"] == "SALES_PERSON"


def test_user_cannot_change_roles(client, user_token):
    resp = client.put(
        "/api/admin/users/000000000000000000000000/role",
        json={"role": "ADMIN"},
        headers=auth_header(user_token),
    )
    assert resp.status_code == 403


def test_user_cannot_access_sales_dashboard(client, user_token):
    resp = client.get("/api/sales/products", headers=auth_header(user_token))
    assert resp.status_code == 403


def test_admin_cannot_use_sales_only_route(client, admin_token):
    # require_sales_person is strict to SALES_PERSON only, by design.
    resp = client.get("/api/sales/products", headers=auth_header(admin_token))
    assert resp.status_code == 403


def test_expired_token_rejected(client, app):
    import jwt as pyjwt
    from datetime import datetime, timedelta, timezone

    from app.config import config
    from app.models.user import find_user_by_email
    from tests.conftest import register

    register(client, "Expired", "expired@test.com", "Password1")
    user = find_user_by_email("expired@test.com")

    expired_payload = {
        "sub": str(user["_id"]),
        "role": "USER",
        "iat": datetime.now(timezone.utc) - timedelta(hours=2),
        "exp": datetime.now(timezone.utc) - timedelta(hours=1),
    }
    expired_token = pyjwt.encode(expired_payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)

    resp = client.get("/api/auth/me", headers=auth_header(expired_token))
    assert resp.status_code == 401
