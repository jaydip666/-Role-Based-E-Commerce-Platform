"""Shared third-party clients (MongoDB, Cloudinary, Razorpay).

Kept in one module so every part of the app talks to the same
initialized client instances instead of constructing their own.
"""
import cloudinary
import razorpay
from pymongo import MongoClient

from app.config import config

_mongo_client = None
_db = None


def init_mongo():
    global _mongo_client, _db
    _mongo_client = MongoClient(config.MONGODB_URI)
    _db = _mongo_client[config.MONGODB_DB_NAME]
    return _db


def get_db():
    if _db is None:
        return init_mongo()
    return _db


def set_db(db):
    """Injects an already-constructed database (used by the test suite to
    supply an isolated mongomock instance instead of a real MongoDB)."""
    global _db
    _db = db
    return _db


def init_cloudinary():
    cloudinary.config(
        cloud_name=config.CLOUDINARY_CLOUD_NAME,
        api_key=config.CLOUDINARY_API_KEY,
        api_secret=config.CLOUDINARY_API_SECRET,
        secure=True,
    )


def get_razorpay_client():
    return razorpay.Client(auth=(config.RAZORPAY_KEY_ID, config.RAZORPAY_KEY_SECRET))
