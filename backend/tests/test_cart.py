from tests.conftest import auth_header


def _make_product(client, sales_token, stock=10, price=100):
    resp = client.post(
        "/api/products",
        json={
            "name": "Cart Item",
            "description": "desc",
            "price": price,
            "category": "Misc",
            "stock": stock,
            "image_url": "https://res.cloudinary.com/demo/image/upload/v1/x.jpg",
        },
        headers=auth_header(sales_token),
    )
    return resp.get_json()["data"]["product"]


def test_cart_requires_auth(client):
    resp = client.get("/api/cart")
    assert resp.status_code == 401


def test_add_item_to_cart(client, sales_token, user_token):
    product = _make_product(client, sales_token)
    resp = client.post(
        "/api/cart", json={"product_id": product["id"], "quantity": 2}, headers=auth_header(user_token)
    )
    assert resp.status_code == 201
    data = resp.get_json()["data"]
    assert data["item_count"] == 2
    assert data["subtotal"] == 200


def test_add_item_beyond_stock_rejected(client, sales_token, user_token):
    product = _make_product(client, sales_token, stock=3)
    resp = client.post(
        "/api/cart", json={"product_id": product["id"], "quantity": 10}, headers=auth_header(user_token)
    )
    assert resp.status_code == 409


def test_update_quantity(client, sales_token, user_token):
    product = _make_product(client, sales_token)
    client.post("/api/cart", json={"product_id": product["id"], "quantity": 1}, headers=auth_header(user_token))
    resp = client.put(
        f"/api/cart/{product['id']}", json={"quantity": 5}, headers=auth_header(user_token)
    )
    assert resp.status_code == 200
    assert resp.get_json()["data"]["item_count"] == 5


def test_decrease_quantity(client, sales_token, user_token):
    product = _make_product(client, sales_token)
    client.post("/api/cart", json={"product_id": product["id"], "quantity": 5}, headers=auth_header(user_token))
    resp = client.put(
        f"/api/cart/{product['id']}", json={"quantity": 2}, headers=auth_header(user_token)
    )
    assert resp.get_json()["data"]["item_count"] == 2


def test_remove_item(client, sales_token, user_token):
    product = _make_product(client, sales_token)
    client.post("/api/cart", json={"product_id": product["id"], "quantity": 1}, headers=auth_header(user_token))
    resp = client.delete(f"/api/cart/{product['id']}", headers=auth_header(user_token))
    assert resp.status_code == 200
    assert resp.get_json()["data"]["item_count"] == 0


def test_cart_total_with_multiple_items(client, sales_token, user_token):
    p1 = _make_product(client, sales_token, price=100)
    p2 = _make_product(client, sales_token, price=250)
    client.post("/api/cart", json={"product_id": p1["id"], "quantity": 2}, headers=auth_header(user_token))
    resp = client.post(
        "/api/cart", json={"product_id": p2["id"], "quantity": 1}, headers=auth_header(user_token)
    )
    assert resp.get_json()["data"]["total"] == 450
