from datetime import timedelta
from pathlib import Path

from environs import Env

from config import settings

env = Env()
env.read_env()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = env.str("SECRET_KEY")

DEBUG = True

ALLOWED_HOSTS = ["http://localhost"]


INSTALLED_APPS = settings.INSTALLED_APPS

MIDDLEWARE = settings.MIDDLEWARE

ROOT_URLCONF = settings.ROOT_URLCONF

TEMPLATES = settings.TEMPLATES

WSGI_APPLICATION = settings.WSGI_APPLICATION

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}


AUTH_PASSWORD_VALIDATORS = settings.AUTH_PASSWORD_VALIDATORS


LANGUAGE_CODE = settings.LANGUAGE_CODE

TIME_ZONE = settings.TIME_ZONE

USE_I18N = settings.USE_I18N

USE_TZ = settings.USE_TZ


DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
MEDIA_ROOT = BASE_DIR / "test_media"
MEDIA_URL = "/media/"

DEFAULT_AUTO_FIELD = settings.DEFAULT_AUTO_FIELD

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = ["http://localhost:3000", "http://localhost:8000"]
CSRF_TRUSTED_ORIGINS = ["http://localhost:3000", "http://localhost:8000"]

REST_FRAMEWORK = settings.REST_FRAMEWORK
REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {}

SPECTACULAR_SETTINGS = settings.SPECTACULAR_SETTINGS

AUTH_USER_MODEL = "users.User"

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "TOKEN_OBTAIN_SERIALIZER": "users.serializers.TokenObtainPairSerializer",
}

ALLOWED_EMAIL_DOMAINS = ["icog.et"]
FRONTEND_DOMAIN = "task-tracker.icog.et"
SITE_NAME = "task-tracker"
SITE_ID = 1

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "user"
EMAIL_HOST_PASSWORD = "password"  # noqa: S105
DEFAULT_FROM_EMAIL = f"noreply@{FRONTEND_DOMAIN}"

DJOSER = settings.DJOSER
DJOSER["SOCIAL_AUTH_ALLOWED_REDIRECT_URIS"] = ["http://localhost:3000"]

AUTHENTICATION_BACKENDS = (
    "axes.backends.AxesBackend",
    "django.contrib.auth.backends.ModelBackend",
)
