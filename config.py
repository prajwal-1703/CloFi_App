import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", os.urandom(32))
    # SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "mysql://root:@localhost:3306/secure_donation_db")
    SQLALCHEMY_DATABASE_URI = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:DevConnect%40108@localhost:3306/secure_donation_db"
)

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session & cookies
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "False") == "True"
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # Rate limiting default
    RATE_LIMIT_DEFAULT = os.getenv("RATE_LIMIT_DEFAULT", "200 per hour")

    # Talisman Security
    TALISMAN_FORCE_HTTPS = False  # enable behind HTTPS/Proxy
    TALISMAN_CONTENT_SECURITY_POLICY = {
        'default-src': ["'self'"],
        'img-src': ["'self'", "data:"],
        'style-src': ["'self'", "'unsafe-inline'"],
        'script-src': ["'self'"],
        'object-src': ["'none'"],
        'frame-ancestors': ["'self'"],
        'base-uri': ["'self'"],
        'form-action': ["'self'"],
    }
