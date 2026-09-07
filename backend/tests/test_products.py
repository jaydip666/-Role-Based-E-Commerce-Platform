from tests.conftest import auth_header


def create_product(client, token, **overrides):
    payload = {
        "name": "Test Shirt",
        "description": "A comfortable cotton shirt",
        "price": 500,
        "category": "Apparel",
        "stock": 10,
        "image_url": "https://res.cloudinary.com/demo/image/upload/v1/shirt.jpg",
    }
    payload.update(overrides)
    return client.post("/api/products", json=payload, headers=auth_header(token))


def test_sales_person_can_create_product(client, sales_token):
    resp = create_product(client, sales_token)
    assert resp.status_code == 201
    assert resp.get_json()["data"]["product"]["name"] == "Test Shirt"


def test_user_cannot_create_product(client, user_token):
    resp = create_product(client, user_token)
    assert resp.status_code == 403


def test_create_product_requires_auth(client):
    resp = client.post("/api/products", json={"name": "x"})
    assert resp.status_code == 401


def test_create_product_validation_error(client, sales_token):
    resp = create_product(client, sales_token, name="")
    assert resp.status_code == 400


def test_public_can_list_and_get_product(client, sales_token):
    created = create_product(client, sales_token).get_json()["data"]["product"]
    resp = client.get("/api/products")
    assert resp.status_code == 200
    assert resp.get_json()["data"]["count"] >= 1

    resp2 = client.get(f"/api/products/{created['id']}")
    assert resp2.status_code == 200
    assert resp2.get_json()["data"]["product"]["id"] == created["id"]


def test_search_filters_by_keyword(client, sales_token):
    create_product(client, sales_token, name="Blue Denim Jacket", category="Apparel")
    create_product(client, sales_token, name="Bluetooth Speaker", category="Electronics")

    resp = client.get("/api/products?search=denim")
    products = resp.get_json()["data"]["products"]
    assert len(products) == 1
    assert products[0]["name"] == "Blue Denim Jacket"


def test_category_filter(client, sales_token):
    create_product(client, sales_token, name="Sofa", category="Furniture")
    create_product(client, sales_token, name="Lamp", category="Home")

    resp = client.get("/api/products?category=Furniture")
    products = resp.get_json()["data"]["products"]
    assert len(products) == 1
    assert products[0]["category"] == "Furniture"


def test_price_range_filter(client, sales_token):
    create_product(client, sales_token, name="Cheap Item", price=50)
    create_product(client, sales_token, name="Mid Item", price=500)
    create_product(client, sales_token, name="Expensive Item", price=5000)

    resp = client.get("/api/products?minPrice=100&maxPrice=1000")
    products = resp.get_json()["data"]["products"]
    names = {p["name"] for p in products}
    assert names == {"Mid Item"}


def test_sales_person_can_edit_own_product(client, sales_token):
    created = create_product(client, sales_token).get_json()["data"]["product"]
    resp = client.put(
        f"/api/products/{created['id']}", json={"price": 999}, headers=auth_header(sales_token)
    )
    assert resp.status_code == 200
    assert resp.get_json()["data"]["product"]["price"] == 999


def test_sales_person_cannot_edit_others_product(client, sales_token, sales_token_2):
    created = create_product(client, sales_token).get_json()["data"]["product"]
    resp = client.put(
        f"/api/products/{created['id']}", json={"price": 1}, headers=auth_header(sales_token_2)
    )
    assert resp.status_code == 403


def test_sales_person_cannot_delete_others_product(client, sales_token, sales_token_2):
    created = create_product(client, sales_token).get_json()["data"]["product"]
    resp = client.delete(f"/api/products/{created['id']}", headers=auth_header(sales_token_2))
    assert resp.status_code == 403


def test_sales_person_can_delete_own_product(client, sales_token):
    created = create_product(client, sales_token).get_json()["data"]["product"]
    resp = client.delete(f"/api/products/{created['id']}", headers=auth_header(sales_token))
    assert resp.status_code == 200


def test_admin_can_edit_any_product(client, sales_token, admin_token):
    created = create_product(client, sales_token).get_json()["data"]["product"]
    resp = client.put(
        f"/api/products/{created['id']}", json={"price": 42}, headers=auth_header(admin_token)
    )
    assert resp.status_code == 200
    assert resp.get_json()["data"]["product"]["price"] == 42


def test_admin_can_delete_any_product(client, sales_token, admin_token):
    created = create_product(client, sales_token).get_json()["data"]["product"]
    resp = client.delete(f"/api/products/{created['id']}", headers=auth_header(admin_token))
    assert resp.status_code == 200


def test_user_cannot_delete_product(client, sales_token, user_token):
    created = create_product(client, sales_token).get_json()["data"]["product"]
    resp = client.delete(f"/api/products/{created['id']}", headers=auth_header(user_token))
    assert resp.status_code == 403
