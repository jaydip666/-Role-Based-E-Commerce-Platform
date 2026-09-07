from tests.conftest import auth_header


def _make_product(client, sales_token, stock=10, price=100):
    resp = client.post(
        "/api/products",
        json={
            "name": "Payment Item",
            "description": "desc",
            "price": price,
            "category": "Misc",
            "stock": stock,
            "image_url": "https://res.cloudinary.com/demo/image/upload/v1/x.jpg",
        },
        headers=auth_header(sales_token),
    )
    return resp.get_json()["data"]["product"]


def _fake_razorpay_order(amount_in_rupees, receipt):
    return {"id": "order_FAKE123", "amount": int(amount_in_rupees * 100), "currency": "INR"}


def test_create_order_requires_nonempty_cart(client, user_token):
    resp = client.post("/api/payment/create-order", headers=auth_header(user_token))
    assert resp.status_code == 400


def test_create_order_computes_amount_from_db_not_client(client, sales_token, user_token, monkeypatch):
    product = _make_product(client, sales_token, price=150)
    client.post("/api/cart", json={"product_id": product["id"], "quantity": 3}, headers=auth_header(user_token))

    monkeypatch.setattr("app.controllers.payment_controller.create_razorpay_order", _fake_razorpay_order)

    resp = client.post("/api/payment/create-order", headers=auth_header(user_token))
    assert resp.status_code == 201
    data = resp.get_json()["data"]
    # 3 * 150 = 450 rupees = 45000 paise, regardless of any client-supplied amount
    assert data["amount"] == 45000
    assert data["razorpay_order_id"] == "order_FAKE123"


def test_verify_invalid_signature_rejected(client, sales_token, user_token, monkeypatch):
    product = _make_product(client, sales_token, price=100)
    client.post("/api/cart", json={"product_id": product["id"], "quantity": 1}, headers=auth_header(user_token))
    monkeypatch.setattr("app.controllers.payment_controller.create_razorpay_order", _fake_razorpay_order)
    client.post("/api/payment/create-order", headers=auth_header(user_token))

    monkeypatch.setattr(
        "app.controllers.payment_controller.verify_payment_signature", lambda *a, **k: False
    )
    resp = client.post(
        "/api/payment/verify",
        json={
            "razorpay_order_id": "order_FAKE123",
            "razorpay_payment_id": "pay_FAKE456",
            "razorpay_signature": "bad_signature",
        },
        headers=auth_header(user_token),
    )
    assert resp.status_code == 400

    orders_resp = client.get("/api/orders", headers=auth_header(user_token))
    assert orders_resp.get_json()["data"]["count"] == 0


def test_verify_valid_signature_creates_order_and_clears_cart(client, sales_token, user_token, monkeypatch):
    product = _make_product(client, sales_token, price=200, stock=10)
    client.post("/api/cart", json={"product_id": product["id"], "quantity": 2}, headers=auth_header(user_token))
    monkeypatch.setattr("app.controllers.payment_controller.create_razorpay_order", _fake_razorpay_order)
    client.post("/api/payment/create-order", headers=auth_header(user_token))

    monkeypatch.setattr(
        "app.controllers.payment_controller.verify_payment_signature", lambda *a, **k: True
    )
    resp = client.post(
        "/api/payment/verify",
        json={
            "razorpay_order_id": "order_FAKE123",
            "razorpay_payment_id": "pay_FAKE456",
            "razorpay_signature": "good_signature",
        },
        headers=auth_header(user_token),
    )
    assert resp.status_code == 201
    order = resp.get_json()["data"]["order"]
    assert order["payment_status"] == "paid"
    assert order["total_amount"] == 400

    cart_resp = client.get("/api/cart", headers=auth_header(user_token))
    assert cart_resp.get_json()["data"]["item_count"] == 0

    orders_resp = client.get("/api/orders", headers=auth_header(user_token))
    assert orders_resp.get_json()["data"]["count"] == 1
