from .base import *

ALLOWED_HOSTS = ["yourdomain.com", "www.yourdomain.com"]

CSRF_TRUSTED_ORIGINS = ["https://yourdomain.com"]


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "mydatabase",
        "USER": "myuser",
        "PASSWORD": "mypassword",
        "HOST": "localhost",
        "PORT": "5432",
    }
}
