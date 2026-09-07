"""Tests for the Cloudinary image-upload integration.

No real Cloudinary credentials are configured in this environment (see
backend/.env.example — CLOUDINARY_* are blank placeholders), so these tests
mock only the third-party network boundary (`cloudinary.uploader.upload`)
and exercise our own integration code for real: extension/size validation,
error propagation, and — most importantly — that only the returned
`secure_url` string ever gets persisted to MongoDB, never raw file bytes.

Verifying against a real Cloudinary account requires populating
CLOUDINARY_CLOUD_NAME / CLOUDINARY_API_KEY / CLOUDINARY_API_SECRET with
real values, which cannot be fabricated here.
"""
import io

import pytest

from app.services.cloudinary_service import ImageUploadError, upload_product_image
from tests.conftest import auth_header


class FakeFileStorage:
    """Minimal stand-in for werkzeug's FileStorage."""

    def __init__(self, filename, content=b"fake-image-bytes"):
        self.filename = filename
        self._stream = io.BytesIO(content)

    def seek(self, offset, whence=0):
        return self._stream.seek(offset, whence)

    def tell(self):
        return self._stream.tell()

    def read(self, *args):
        return self._stream.read(*args)


def test_upload_rejects_missing_file():
    with pytest.raises(ImageUploadError, match="No image file"):
        upload_product_image(None)


def test_upload_rejects_disallowed_extension():
    fake_file = FakeFileStorage("malware.exe")
    with pytest.raises(ImageUploadError, match="Unsupported image type"):
        upload_product_image(fake_file)


def test_upload_rejects_oversized_file():
    big_content = b"x" * (5 * 1024 * 1024 + 1)
    fake_file = FakeFileStorage("big.png", content=big_content)
    with pytest.raises(ImageUploadError, match="5MB size limit"):
        upload_product_image(fake_file)


def test_upload_calls_cloudinary_and_returns_secure_url(monkeypatch):
    captured = {}

    def fake_upload(file_storage, **kwargs):
        captured["kwargs"] = kwargs
        captured["file_storage"] = file_storage
        return {"secure_url": "https://res.cloudinary.com/demo/image/upload/v1/fake123.jpg"}

    monkeypatch.setattr("app.services.cloudinary_service.cloudinary.uploader.upload", fake_upload)

    fake_file = FakeFileStorage("product.png")
    url = upload_product_image(fake_file)

    assert url == "https://res.cloudinary.com/demo/image/upload/v1/fake123.jpg"
    assert captured["kwargs"]["folder"] == "ecommerce_internship/products"
    assert captured["kwargs"]["resource_type"] == "image"
    assert captured["file_storage"] is fake_file


def test_upload_wraps_cloudinary_errors(monkeypatch):
    def fake_upload(file_storage, **kwargs):
        raise RuntimeError("network timeout")

    monkeypatch.setattr("app.services.cloudinary_service.cloudinary.uploader.upload", fake_upload)

    fake_file = FakeFileStorage("product.png")
    with pytest.raises(ImageUploadError, match="Cloudinary upload failed"):
        upload_product_image(fake_file)


def test_create_product_with_file_upload_stores_only_url_in_mongo(client, sales_token, monkeypatch):
    """End-to-end through the real /api/products route: a multipart image
    upload must result in a MongoDB document that stores nothing but the
    Cloudinary secure_url string — never raw bytes.
    """

    def fake_upload(file_storage, **kwargs):
        return {"secure_url": "https://res.cloudinary.com/demo/image/upload/v1/realish.jpg"}

    monkeypatch.setattr("app.services.cloudinary_service.cloudinary.uploader.upload", fake_upload)

    data = {
        "name": "Uploaded Product",
        "description": "Has a real uploaded image",
        "price": "300",
        "category": "Misc",
        "stock": "5",
        "image": (io.BytesIO(b"\x89PNG\r\n\x1a\nfakepngbytes"), "photo.png"),
    }
    resp = client.post(
        "/api/products",
        data=data,
        content_type="multipart/form-data",
        headers=auth_header(sales_token),
    )
    assert resp.status_code == 201
    product = resp.get_json()["data"]["product"]
    assert product["image_url"] == "https://res.cloudinary.com/demo/image/upload/v1/realish.jpg"

    from app.models.product import products_collection
    from bson import ObjectId

    stored = products_collection().find_one({"_id": ObjectId(product["id"])})
    assert stored["image_url"] == "https://res.cloudinary.com/demo/image/upload/v1/realish.jpg"
    assert isinstance(stored["image_url"], str)
    # No raw binary/image payload field of any kind on the document.
    assert not any(key for key in stored.keys() if "image_data" in key or "file" in key.lower())


def test_create_product_without_image_or_url_rejected(client, sales_token):
    resp = client.post(
        "/api/products",
        json={"name": "No Image", "description": "d", "price": 10, "category": "Misc", "stock": 1},
        headers=auth_header(sales_token),
    )
    assert resp.status_code == 400
