from bson import ObjectId
from bson.errors import InvalidId


def to_object_id(value):
    """Returns a bson.ObjectId or None if value is not a valid id."""
    try:
        return ObjectId(str(value))
    except (InvalidId, TypeError):
        return None
