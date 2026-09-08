"""Development seed script.

Creates three test accounts (admin / sales person / user) and a handful of
sample products so the app can be exercised end to end without manually
registering accounts first.

Usage:
    python seed.py

Safe to re-run: existing seeded accounts/products are left untouched.
"""
from app import create_app
from app.models.product import new_product_document, products_collection
from app.models.roles import ADMIN, SALES_PERSON, USER
from app.models.user import create_user, find_user_by_email
from app.utils.security import hash_password

TEST_USERS = [
    {"name": "Admin User", "email": "admin@example.com", "password": "Admin@123", "role": ADMIN},
    {"name": "Sales Person", "email": "sales@example.com", "password": "Sales@123", "role": SALES_PERSON},
    {"name": "Customer", "email": "user@example.com", "password": "User@1234", "role": USER},
]

SAMPLE_PRODUCTS = [
    {
        "name": "Wireless Headphones",
        "description": "Over-ear Bluetooth headphones with noise cancellation.",
        "price": 2499,
        "category": "Electronics",
        "image_url": "https://res.cloudinary.com/demo/image/upload/v1/samples/ecommerce/headphones.jpg",
        "stock": 25,
    },
    {
        "name": "Cotton T-Shirt",
        "description": "Breathable 100% cotton crew-neck t-shirt.",
        "price": 499,
        "category": "Apparel",
        "image_url": "https://res.cloudinary.com/demo/image/upload/v1/samples/ecommerce/shirt.jpg",
        "stock": 100,
    },
    {
        "name": "Stainless Steel Bottle",
        "description": "1L vacuum-insulated stainless steel water bottle.",
        "price": 799,
        "category": "Home",
        "image_url": "https://res.cloudinary.com/demo/image/upload/v1/samples/ecommerce/bottle.jpg",
        "stock": 60,
    },
]


def run():
    app = create_app()
    with app.app_context():
        created_users = {}
        for u in TEST_USERS:
            existing = find_user_by_email(u["email"])
            if existing:
                created_users[u["role"]] = existing
                print(f"[skip] {u['email']} already exists")
                continue
            user = create_user(
                name=u["name"], email=u["email"], password_hash=hash_password(u["password"]), role=u["role"]
            )
            created_users[u["role"]] = user
            print(f"[created] {u['email']} / {u['password']} ({u['role']})")

        sales_user = created_users[SALES_PERSON]
        for p in SAMPLE_PRODUCTS:
            if products_collection().find_one({"name": p["name"]}):
                print(f"[skip] product '{p['name']}' already exists")
                continue
            doc = new_product_document(
                name=p["name"],
                description=p["description"],
                price=p["price"],
                category=p["category"],
                image_url=p["image_url"],
                owner_id=sales_user["_id"],
                owner_name=sales_user["name"],
                stock=p["stock"],
            )
            products_collection().insert_one(doc)
            print(f"[created] product '{p['name']}'")

    print("\nSeed complete. Test credentials:")
    for u in TEST_USERS:
        print(f"  {u['role']:<13} {u['email']:<20} {u['password']}")


if __name__ == "__main__":
    run()
