from tests.conftest import auth_header


def _make_product(client, sales_token, name="Order Item", price=100, stock=10):
    resp = client.post(
        "/api/products",
        json={
            "name": name,
            "description": "desc",
            "price": price,
            "category": "Misc",
            "stock": stock,
            "image_url": "https://res.cloudinary.com/demo/image/upload/v1/x.jpg",
        },
        headers=auth_header(sales_token),
    )
    return resp.get_json()["data"]["product"]


def _pay_for_cart(client, user_token, monkeypatch, order_id="order_ORD1"):
    monkeypatch.setattr(
        "app.controllers.payment_controller.create_razorpay_order",
        lambda amount, receipt: {"id": order_id, "amount": int(amount * 100), "currency": "INR"},
    )
    client.post("/api/payment/create-order", headers=auth_header(user_token))
    monkeypatch.setattr("app.controllers.payment_controller.verify_payment_signature", lambda *a, **k: True)
    resp = client.post(
        "/api/payment/verify",
        json={
            "razorpay_order_id": order_id,
            "razorpay_payment_id": f"pay_{order_id}",
            "razorpay_signature": "sig",
        },
        headers=auth_header(user_token),
    )
    return resp.get_json()["data"]["order"]


def test_user_sees_only_own_orders(client, sales_token, user_token, monkeypatch):
    from tests.conftest import login, register

    register(client, "Second User", "second@test.com", "Password1")
    second_token = login(client, "second@test.com", "Password1").get_json()["data"]["token"]

    product = _make_product(client, sales_token)
    client.post("/api/cart", json={"product_id": product["id"], "quantity": 1}, headers=auth_header(user_token))
    _pay_for_cart(client, user_token, monkeypatch, order_id="order_USER1")

    product2 = _make_product(client, sales_token, name="Second Item")
    client.post(
        "/api/cart", json={"product_id": product2["id"], "quantity": 1}, headers=auth_header(second_token)
    )
    _pay_for_cart(client, second_token, monkeypatch, order_id="order_USER2")

    resp = client.get("/api/orders", headers=auth_header(user_token))
    orders = resp.get_json()["data"]["orders"]
    assert len(orders) == 1
    assert orders[0]["razorpay_order_id"] == "order_USER1"


def test_user_cannot_view_another_users_order_by_id(client, sales_token, user_token, monkeypatch):
    from tests.conftest import login, register

    register(client, "Third User", "third@test.com", "Password1")
    other_token = login(client, "third@test.com", "Password1").get_json()["data"]["token"]

    product = _make_product(client, sales_token)
    client.post("/api/cart", json={"product_id": product["id"], "quantity": 1}, headers=auth_header(user_token))
    order = _pay_for_cart(client, user_token, monkeypatch, order_id="order_PRIVATE")

    resp = client.get(f"/api/orders/{order['id']}", headers=auth_header(other_token))
    assert resp.status_code == 403


def test_sales_person_sees_only_relevant_orders(client, sales_token, sales_token_2, user_token, monkeypatch):
    product_a = _make_product(client, sales_token, name="Seller A Item")
    product_b = _make_product(client, sales_token_2, name="Seller B Item")

    client.post("/api/cart", json={"product_id": product_a["id"], "quantity": 1}, headers=auth_header(user_token))
    client.post("/api/cart", json={"product_id": product_b["id"], "quantity": 1}, headers=auth_header(user_token))
    _pay_for_cart(client, user_token, monkeypatch, order_id="order_MIXED")

    resp_a = client.get("/api/sales/orders", headers=auth_header(sales_token))
    orders_a = resp_a.get_json()["data"]["orders"]
    assert len(orders_a) == 1
    assert all(item["product_id"] == product_a["id"] for item in orders_a[0]["items"])

    resp_b = client.get("/api/sales/orders", headers=auth_header(sales_token_2))
    orders_b = resp_b.get_json()["data"]["orders"]
    assert len(orders_b) == 1
    assert all(item["product_id"] == product_b["id"] for item in orders_b[0]["items"])


def test_sales_person_does_not_see_unrelated_orders(client, sales_token, sales_token_2, user_token, monkeypatch):
    product_b = _make_product(client, sales_token_2, name="Only Seller B")
    client.post("/api/cart", json={"product_id": product_b["id"], "quantity": 1}, headers=auth_header(user_token))
    _pay_for_cart(client, user_token, monkeypatch, order_id="order_B_ONLY")

    resp_a = client.get("/api/sales/orders", headers=auth_header(sales_token))
    assert resp_a.get_json()["data"]["count"] == 0


def test_admin_sees_all_orders(client, sales_token, sales_token_2, user_token, admin_token, monkeypatch):
    product_a = _make_product(client, sales_token, name="Item A")
    product_b = _make_product(client, sales_token_2, name="Item B")
    client.post("/api/cart", json={"product_id": product_a["id"], "quantity": 1}, headers=auth_header(user_token))
    _pay_for_cart(client, user_token, monkeypatch, order_id="order_ALL1")

    client.post("/api/cart", json={"product_id": product_b["id"], "quantity": 1}, headers=auth_header(user_token))
    _pay_for_cart(client, user_token, monkeypatch, order_id="order_ALL2")

    resp = client.get("/api/orders", headers=auth_header(admin_token))
    assert resp.get_json()["data"]["count"] == 2

    admin_resp = client.get("/api/admin/orders", headers=auth_header(admin_token))
    assert admin_resp.get_json()["data"]["count"] == 2


def test_admin_can_update_order_status(client, sales_token, user_token, admin_token, monkeypatch):
    product = _make_product(client, sales_token)
    client.post("/api/cart", json={"product_id": product["id"], "quantity": 1}, headers=auth_header(user_token))
    order = _pay_for_cart(client, user_token, monkeypatch, order_id="order_STATUS")

    resp = client.put(
        f"/api/admin/orders/{order['id']}/status",
        json={"order_status": "Shipped"},
        headers=auth_header(admin_token),
    )
    assert resp.status_code == 200
    assert resp.get_json()["data"]["order"]["order_status"] == "Shipped"


def test_non_admin_cannot_update_order_status(client, sales_token, user_token, monkeypatch):
    product = _make_product(client, sales_token)
    client.post("/api/cart", json={"product_id": product["id"], "quantity": 1}, headers=auth_header(user_token))
    order = _pay_for_cart(client, user_token, monkeypatch, order_id="order_NOADMIN")

    resp = client.put(
        f"/api/admin/orders/{order['id']}/status",
        json={"order_status": "Shipped"},
        headers=auth_header(user_token),
    )
    assert resp.status_code == 403
