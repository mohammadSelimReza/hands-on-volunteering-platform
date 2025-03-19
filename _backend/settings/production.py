from .base import *

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "hands-on-volunteering-platform-or66d8a4v.vercel.app",  # Vercel frontend
    "your-backend-domain.com",  # If deployed backend
]
# CORS & CSRF
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React frontend (development)
    "http://localhost:5173",  # Vite frontend (development)
    "http://127.0.0.1:8000",  # Local Django backend
    "http://localhost:5174",  # Additional dev port
    "https://hands-on-volunteering-platform-or66d8a4v.vercel.app",  # Vercel frontend (production)
]
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:8000",
    "http://localhost:5174",
    "https://hands-on-volunteering-platform-or66d8a4v.vercel.app",  # Vercel frontend (production)
]
DATABASES = {
    "default": {
        "ENGINE": os.getenv("engine"),
        "NAME": os.getenv("dbname"),
        "USER": os.getenv("user"),
        "PASSWORD": os.getenv("DB_PASS"),
        "HOST": os.getenv("host"),
        "PORT": os.getenv("port"),
    }
}

# CACHES:
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",  # In-memory cache
        "LOCATION": "unique-snowflake",
    }
}

# Secure settings for production
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
