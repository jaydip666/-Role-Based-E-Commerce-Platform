import cloudinary.uploader

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5MB


class ImageUploadError(Exception):
    pass


def _has_allowed_extension(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_product_image(file_storage):
    """Uploads a Flask FileStorage image to Cloudinary and returns the secure URL.

    Only the resulting Cloudinary URL is ever persisted to MongoDB — the raw
    file bytes are streamed straight through to Cloudinary and never written
    to local disk or the database.
    """
    if not file_storage or not file_storage.filename:
        raise ImageUploadError("No image file provided")

    if not _has_allowed_extension(file_storage.filename):
        raise ImageUploadError("Unsupported image type. Allowed: png, jpg, jpeg, gif, webp")

    file_storage.seek(0, 2)  # seek to end
    size = file_storage.tell()
    file_storage.seek(0)
    if size > MAX_FILE_SIZE_BYTES:
        raise ImageUploadError("Image exceeds the 5MB size limit")

    try:
        result = cloudinary.uploader.upload(
            file_storage,
            folder="ecommerce_internship/products",
            resource_type="image",
        )
    except Exception as exc:  # cloudinary raises generic errors
        raise ImageUploadError(f"Cloudinary upload failed: {exc}") from exc

    return result.get("secure_url")
