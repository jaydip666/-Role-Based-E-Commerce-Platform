import uuid

import mongomock
import pytest


@pytest.fixture()
def app(monkeypatch):
    # mongomock shares an in-memory "server" store across MongoClient
    # instances that connect to the same default host, which would leak
    # data between tests. A unique host string per test gives each test
    # function its own isolated in-memory database.
    test_client = mongomock.MongoClient(f"mongodb://{uuid.uuid4().hex}")
    test_db = test_client["ecommerce_test"]

    from app import extensions

    monkeypatch.setattr(extensions, "init_cloudinary", lambda: None)

    from app import create_app

    # Passing db= injects the isolated mongomock instance directly, instead
    # of create_app() connecting to the real MONGODB_URI.
    flask_app = create_app(db=test_db)
    flask_app.config.update(TESTING=True)
    yield flask_app


@pytest.fixture()
def client(app):
    return app.test_client()


def register(client, name, email, password):
    return client.post("/api/auth/register", json={"name": name, "email": email, "password": password})


def login(client, email, password):
    return client.post("/api/auth/login", json={"email": email, "password": password})


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def admin_token(client):
    register(client, "Admin", "admin@test.com", "Admin@123")
    # Promote the freshly registered user to ADMIN directly via the DB layer.
    from app.models.roles import ADMIN
    from app.models.user import find_user_by_email, users_collection

    user = find_user_by_email("admin@test.com")
    users_collection().update_one({"_id": user["_id"]}, {"$set": {"role": ADMIN}})
    resp = login(client, "admin@test.com", "Admin@123")
    return resp.get_json()["data"]["token"]


@pytest.fixture()
def sales_token(client):
    register(client, "Seller One", "seller1@test.com", "Seller@123")
    from app.models.roles import SALES_PERSON
    from app.models.user import find_user_by_email, users_collection

    user = find_user_by_email("seller1@test.com")
    users_collection().update_one({"_id": user["_id"]}, {"$set": {"role": SALES_PERSON}})
    resp = login(client, "seller1@test.com", "Seller@123")
    return resp.get_json()["data"]["token"]


@pytest.fixture()
def sales_token_2(client):
    register(client, "Seller Two", "seller2@test.com", "Seller@123")
    from app.models.roles import SALES_PERSON
    from app.models.user import find_user_by_email, users_collection

    user = find_user_by_email("seller2@test.com")
    users_collection().update_one({"_id": user["_id"]}, {"$set": {"role": SALES_PERSON}})
    resp = login(client, "seller2@test.com", "Seller@123")
    return resp.get_json()["data"]["token"]


@pytest.fixture()
def user_token(client):
    register(client, "Regular User", "user@test.com", "User@1234")
    resp = login(client, "user@test.com", "User@1234")
    return resp.get_json()["data"]["token"]
