from tests.conftest import auth_header


def _make_product(client, sales_token):
    resp = client.post(
        "/api/products",
        json={
            "name": "Wishlist Item",
            "description": "desc",
            "price": 100,
            "category": "Misc",
            "stock": 5,
            "image_url": "https://res.cloudinary.com/demo/image/upload/v1/x.jpg",
        },
        headers=auth_header(sales_token),
    )
    return resp.get_json()["data"]["product"]


def test_wishlist_requires_auth(client):
    resp = client.get("/api/wishlist")
    assert resp.status_code == 401


def test_add_and_view_wishlist(client, sales_token, user_token):
    product = _make_product(client, sales_token)
    add_resp = client.post(
        "/api/wishlist", json={"product_id": product["id"]}, headers=auth_header(user_token)
    )
    assert add_resp.status_code == 201

    view_resp = client.get("/api/wishlist", headers=auth_header(user_token))
    products = view_resp.get_json()["data"]["products"]
    assert len(products) == 1
    assert products[0]["id"] == product["id"]


def test_wishlist_prevents_duplicates(client, sales_token, user_token):
    product = _make_product(client, sales_token)
    for _ in range(3):
        client.post("/api/wishlist", json={"product_id": product["id"]}, headers=auth_header(user_token))

    view_resp = client.get("/api/wishlist", headers=auth_header(user_token))
    assert view_resp.get_json()["data"]["count"] == 1


def test_remove_from_wishlist(client, sales_token, user_token):
    product = _make_product(client, sales_token)
    client.post("/api/wishlist", json={"product_id": product["id"]}, headers=auth_header(user_token))

    del_resp = client.delete(f"/api/wishlist/{product['id']}", headers=auth_header(user_token))
    assert del_resp.status_code == 200

    view_resp = client.get("/api/wishlist", headers=auth_header(user_token))
    assert view_resp.get_json()["data"]["count"] == 0
