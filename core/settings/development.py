from .base import *

DEBUG = True


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = "smtp4dev"
EMAIL_PORT = 25

EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""

EMAIL_USE_TLS = False
