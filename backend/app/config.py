import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Central application configuration, sourced entirely from environment
    variables so no secret is ever hardcoded in source."""

    PORT = int(os.environ.get("PORT", 5000))
    FLASK_ENV = os.environ.get("FLASK_ENV", "development")
    DEBUG = FLASK_ENV == "development"

    MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DB_NAME = os.environ.get("MONGODB_DB_NAME", "ecommerce_internship")

    JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret-change-me")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRES_HOURS = int(os.environ.get("JWT_EXPIRES_HOURS", 24))

    CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY = os.environ.get("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET", "")

    RAZORPAY_KEY_ID = os.environ.get("RAZORPAY_KEY_ID", "")
    RAZORPAY_KEY_SECRET = os.environ.get("RAZORPAY_KEY_SECRET", "")

    CLIENT_URL = os.environ.get("CLIENT_URL", "http://localhost:5173")

    @property
    def CORS_ORIGINS(self):
        # Support a comma-separated list so multiple frontend origins
        # (e.g. local dev + deployed Vercel URL) can be allowed at once.
        return [origin.strip() for origin in self.CLIENT_URL.split(",") if origin.strip()]


config = Config()
