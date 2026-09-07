from flask import g

from app.models.product import new_product_document, products_collection, serialize_product
from app.models.roles import ADMIN
from app.services.cloudinary_service import ImageUploadError, upload_product_image
from app.utils.object_id import to_object_id
from app.utils.responses import error, success
from app.validators.validators import validate_product_payload


def list_products(args):
    query = {}

    search = args.get("search", "").strip()
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
        ]

    category = args.get("category", "").strip()
    if category:
        query["category"] = {"$regex": f"^{category}$", "$options": "i"}

    min_price = args.get("minPrice")
    max_price = args.get("maxPrice")
    price_query = {}
    if min_price not in (None, ""):
        try:
            price_query["$gte"] = float(min_price)
        except ValueError:
            return error("minPrice must be a number", 400)
    if max_price not in (None, ""):
        try:
            price_query["$lte"] = float(max_price)
        except ValueError:
            return error("maxPrice must be a number", 400)
    if price_query:
        query["price"] = price_query

    owner_id = args.get("owner_id")
    if owner_id:
        owner_object_id = to_object_id(owner_id)
        if not owner_object_id:
            return error("Invalid owner_id", 400)
        query["owner_id"] = owner_object_id

    cursor = products_collection().find(query).sort("created_at", -1)
    products = [serialize_product(p) for p in cursor]
    return success({"products": products, "count": len(products)})


def get_product(product_id):
    object_id = to_object_id(product_id)
    if not object_id:
        return error("Invalid product id", 400)
    product = products_collection().find_one({"_id": object_id})
    if not product:
        return error("Product not found", 404)
    return success({"product": serialize_product(product)})


def create_product(form, files):
    errors = validate_product_payload(form)
    if errors:
        return error("Validation failed", 400, errors)

    image_url = None
    image_file = files.get("image")
    if image_file:
        try:
            image_url = upload_product_image(image_file)
        except ImageUploadError as exc:
            return error(str(exc), 400)
    elif form.get("image_url"):
        image_url = form.get("image_url")
    else:
        return error("Validation failed", 400, ["an image file or image_url is required"])

    document = new_product_document(
        name=form["name"].strip(),
        description=form["description"].strip(),
        price=float(form["price"]),
        category=form["category"].strip(),
        image_url=image_url,
        owner_id=g.current_user_id,
        owner_name=g.current_user.get("name"),
        stock=int(form.get("stock", 0)),
    )
    result = products_collection().insert_one(document)
    document["_id"] = result.inserted_id
    return success({"product": serialize_product(document)}, "Product created", 201)


def _find_owned_product_or_error(product_id):
    """Loads a product and enforces ownership: ADMIN may act on any product,
    SALES_PERSON only on products they own. Returns (product, error_response).
    """
    object_id = to_object_id(product_id)
    if not object_id:
        return None, error("Invalid product id", 400)

    product = products_collection().find_one({"_id": object_id})
    if not product:
        return None, error("Product not found", 404)

    if g.current_user_role != ADMIN and product["owner_id"] != g.current_user_id:
        return None, error("You do not have permission to modify this product", 403)

    return product, None


def update_product(product_id, form, files):
    product, err = _find_owned_product_or_error(product_id)
    if err:
        return err

    errors = validate_product_payload(form, partial=True)
    if errors:
        return error("Validation failed", 400, errors)

    updates = {}
    for field in ("name", "description", "category"):
        if field in form and form[field].strip():
            updates[field] = form[field].strip()
    if "price" in form:
        updates["price"] = float(form["price"])
    if "stock" in form:
        updates["stock"] = int(form["stock"])

    image_file = files.get("image")
    if image_file:
        try:
            updates["image_url"] = upload_product_image(image_file)
        except ImageUploadError as exc:
            return error(str(exc), 400)
    elif form.get("image_url"):
        updates["image_url"] = form.get("image_url")

    if not updates:
        return error("No valid fields provided to update", 400)

    from datetime import datetime, timezone
    updates["updated_at"] = datetime.now(timezone.utc)

    products_collection().update_one({"_id": product["_id"]}, {"$set": updates})
    updated = products_collection().find_one({"_id": product["_id"]})
    return success({"product": serialize_product(updated)}, "Product updated")


def delete_product(product_id):
    product, err = _find_owned_product_or_error(product_id)
    if err:
        return err

    products_collection().delete_one({"_id": product["_id"]})
    return success(message="Product deleted")
