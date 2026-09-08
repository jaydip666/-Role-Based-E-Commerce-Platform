from tests.conftest import auth_header


def _make_product(client, sales_token, name="Sales Stats Item", price=100, stock=50):
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


def _pay_for_cart(client, user_token, monkeypatch, order_id="order_STATS1"):
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


def test_sales_person_single_product_stats(client, sales_token, user_token, monkeypatch):
    product = _make_product(client, sales_token, price=200)
    client.post("/api/cart", json={"product_id": product["id"], "quantity": 2}, headers=auth_header(user_token))
    _pay_for_cart(client, user_token, monkeypatch, order_id="order_SINGLE")

    resp = client.get("/api/sales/stats", headers=auth_header(sales_token))
    stats = resp.get_json()["data"]
    assert stats["total_sales"] == 400.0
    assert stats["total_units_sold"] == 2


def test_sales_person_multiple_products_stats_are_summed(client, sales_token, user_token, monkeypatch):
    product_a = _make_product(client, sales_token, name="Product A", price=100)
    product_b = _make_product(client, sales_token, name="Product B", price=150)
    client.post("/api/cart", json={"product_id": product_a["id"], "quantity": 1}, headers=auth_header(user_token))
    client.post("/api/cart", json={"product_id": product_b["id"], "quantity": 1}, headers=auth_header(user_token))
    _pay_for_cart(client, user_token, monkeypatch, order_id="order_MULTI")

    resp = client.get("/api/sales/stats", headers=auth_header(sales_token))
    stats = resp.get_json()["data"]
    assert stats["total_sales"] == 250.0


def test_multi_seller_order_splits_sales_between_sellers(
    client, sales_token, sales_token_2, user_token, admin_token, monkeypatch
):
    product_a = _make_product(client, sales_token, name="Seller A Product", price=10000)
    product_b = _make_product(client, sales_token_2, name="Seller B Product", price=5000)
    client.post("/api/cart", json={"product_id": product_a["id"], "quantity": 1}, headers=auth_header(user_token))
    client.post("/api/cart", json={"product_id": product_b["id"], "quantity": 1}, headers=auth_header(user_token))
    _pay_for_cart(client, user_token, monkeypatch, order_id="order_SPLIT")

    stats_a = client.get("/api/sales/stats", headers=auth_header(sales_token)).get_json()["data"]
    stats_b = client.get("/api/sales/stats", headers=auth_header(sales_token_2)).get_json()["data"]
    assert stats_a["total_sales"] == 10000.0
    assert stats_b["total_sales"] == 5000.0

    # Admin still sees the full order total, not a per-seller split.
    admin_stats = client.get("/api/admin/stats", headers=auth_header(admin_token)).get_json()["data"]
    assert admin_stats["total_sales"] == 15000.0


def test_failed_payment_not_counted_in_sales(client, sales_token, user_token, monkeypatch):
    product = _make_product(client, sales_token, price=999)
    client.post("/api/cart", json={"product_id": product["id"], "quantity": 1}, headers=auth_header(user_token))

    monkeypatch.setattr(
        "app.controllers.payment_controller.create_razorpay_order",
        lambda amount, receipt: {"id": "order_FAIL", "amount": int(amount * 100), "currency": "INR"},
    )
    client.post("/api/payment/create-order", headers=auth_header(user_token))
    monkeypatch.setattr("app.controllers.payment_controller.verify_payment_signature", lambda *a, **k: False)
    resp = client.post(
        "/api/payment/verify",
        json={
            "razorpay_order_id": "order_FAIL",
            "razorpay_payment_id": "pay_order_FAIL",
            "razorpay_signature": "bad-sig",
        },
        headers=auth_header(user_token),
    )
    assert resp.status_code == 400

    stats = client.get("/api/sales/stats", headers=auth_header(sales_token)).get_json()["data"]
    assert stats["total_sales"] == 0.0


def test_sales_person_cannot_manipulate_seller_id_to_inflate_sales(client, sales_token, sales_token_2, user_token, monkeypatch):
    # Only seller B's product is sold; seller A must see zero regardless of
    # anything a client might try to send — stats are derived purely from
    # the authenticated user's id server-side, there is no seller_id input.
    product_b = _make_product(client, sales_token_2, name="B Only", price=777)
    client.post("/api/cart", json={"product_id": product_b["id"], "quantity": 1}, headers=auth_header(user_token))
    _pay_for_cart(client, user_token, monkeypatch, order_id="order_NOINFLATE")

    stats_a = client.get("/api/sales/stats", headers=auth_header(sales_token)).get_json()["data"]
    assert stats_a["total_sales"] == 0.0


def test_user_cannot_access_sales_stats(client, user_token):
    resp = client.get("/api/sales/stats", headers=auth_header(user_token))
    assert resp.status_code == 403
