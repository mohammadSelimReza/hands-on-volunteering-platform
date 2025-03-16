from .base import *

ALLOWED_HOSTS = ["*"]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "postgres",
        "USER": "postgres.kdvnbqqxjjmntgomqsvo",
        "PASSWORD": "Django_database_2025",
        "HOST": "aws-0-ap-southeast-1.pooler.supabase.com",
        "PORT": "6543",
    }
}
