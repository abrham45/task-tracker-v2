from datetime import timedelta
from pathlib import Path

from environs import Env

env = Env()
env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = ["*"]


# Application definition

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "axes",
    "corsheaders",
    "djoser",
    "drf_spectacular",
    "django_filters",
    "minio_storage",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "social_django",
]

LOCAL_APPS = [
    "basedata",
    "core",
    "tasks",
    "users",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "social_django.middleware.SocialAuthExceptionMiddleware",
    "axes.middleware.AxesMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': env.str("DB_ENGINE"),
        'NAME': env.str("DB_NAME"), # Replace with your actual database name
        'USER': env.str("DB_USER"),  # Replace with your actual username
        'PASSWORD': env.str("DB_PASSWORD"),  # Replace with your actual password
        'HOST': env.str("DB_HOST"),  # Use the container's IP
        'PORT': env.str("DB_PORT"),
    }
}
# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Africa/Addis_Ababa"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"


DEFAULT_FILE_STORAGE = "minio_storage.storage.MinioMediaStorage"

MINIO_STORAGE_ENDPOINT = env.str("MINIO_STORAGE_ENDPOINT")
MINIO_STORAGE_USE_HTTPS = env.bool("MINIO_STORAGE_USE_HTTPS", True)

MINIO_STORAGE_ACCESS_KEY = env.str("MINIO_ROOT_USER")
MINIO_STORAGE_SECRET_KEY = env.str("MINIO_ROOT_PASSWORD")

MINIO_STORAGE_MEDIA_BUCKET_NAME = env.str("MINIO_STORAGE_MEDIA_BUCKET_NAME")
MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET = env.bool(
    "MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET", True
)
MINIO_STORAGE_MEDIA_BACKUP_BUCKET = env.str(
    "MINIO_STORAGE_MEDIA_BACKUP_BUCKET", "Recycle bin"
)
MINIO_STORAGE_MEDIA_BACKUP_FORMAT = "backup_%Y-%m-%d_%H-%M-%S_"

protocol = "https" if MINIO_STORAGE_USE_HTTPS else "http"
MINIO_STORAGE_MEDIA_URL = (
    f"{protocol}://{MINIO_STORAGE_ENDPOINT}/{MINIO_STORAGE_MEDIA_BUCKET_NAME}/"
)

MEDIA_URL = MINIO_STORAGE_MEDIA_URL


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = tuple(env.list("CORS_ALLOWED_ORIGINS"))
CSRF_TRUSTED_ORIGINS = tuple(env.list("CSRF_TRUSTED_ORIGINS"))


THROTTLE_RATES = {}


REST_FRAMEWORK = {
    # Throttling settings
    "DEFAULT_THROTTLE_CLASSES": [],
    "DEFAULT_THROTTLE_RATES": THROTTLE_RATES,
    # Pagination settings
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 10,
    # Schema configurations for API documentation
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    # Versioning settings
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
    "DEFAULT_VERSION": env.str("API_DEFAULT_VERSION"),
    "ALLOWED_VERSIONS": env.list("API_ALLOWED_VERSIONS"),
    # Search and Filter settings
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    # Auth settings
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "users.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "core.permissions.CustomDjangoModelPermissions",
    ],
    # Responses handling settings
    "DEFAULT_RENDERER_CLASSES": [
        "core.renderers.JSONRenderer",
    ],
}

SPECTACULAR_SETTINGS = {
    "TITLE": "iCog Task Tracker API",
    "DESCRIPTION": "API documentation for the iCog Task Tracker system.",
    "VERSION": "1.0.0",
    "SCHEMA_PATH_PREFIX": "/api/v[0-9]+",
    "SERVE_INCLUDE_SCHEMA": False,
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "persistAuthorization": True,
    },
    "COMPONENT_SPLIT_REQUEST": True,
    "POSTPROCESSING_HOOKS": ["core.hooks.response_format_hook"],
}

AUTH_USER_MODEL = "users.User"

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "TOKEN_OBTAIN_SERIALIZER": "users.serializers.TokenObtainPairSerializer",
}

ALLOWED_EMAIL_DOMAINS = env.list("ALLOWED_EMAIL_DOMAINS", default=["icog.et"])
FRONTEND_DOMAIN = env.str("FRONTEND_DOMAIN")
SITE_NAME = env.str("SITE_NAME")
SITE_ID = env.int("SITE_ID")

EMAIL_BACKEND = env.str("EMAIL_BACKEND")
EMAIL_HOST = env.str("EMAIL_HOST")
EMAIL_PORT = env.int("EMAIL_PORT")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS")
EMAIL_HOST_USER = env.str("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = f"noreply@{FRONTEND_DOMAIN}"

DJOSER = {
    "SERIALIZERS": {
        "current_user": "users.serializers.UserSerializer",
        "user": "users.serializers.UserSerializer",
        "user_create": "users.serializers.UserCreateSerializer",
    },
    "SEND_ACTIVATION_EMAIL": True,
    "ACTIVATION_URL": f"activate/{{uid}}/{{token}}",
    "PASSWORD_RESET_CONFIRM_URL": (
        f"{FRONTEND_DOMAIN}/password/reset/confirm/{{uid}}/{{token}}/"
    ),
    "SOCIAL_AUTH_TOKEN_STRATEGY": "users.strategies.TokenStrategy",
    "SOCIAL_AUTH_ALLOWED_REDIRECT_URIS": env.list("SOCIAL_AUTH_ALLOWED_REDIRECT_URIS"),
}

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = env("GOOGLE_CLIENT_ID")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = env("GOOGLE_SECRET")
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid",
]
SOCIAL_AUTH_GOOGLE_OAUTH2_EXTRA_DATA = ["first_name", "last_name"]

AUTHENTICATION_BACKENDS = (
    "social_core.backends.google.GoogleOAuth2",
    "axes.backends.AxesBackend",  # needs to be after GoogleOAuth2 to ignore it
    "django.contrib.auth.backends.ModelBackend",
)

DOMAIN = 'task.icogacc.com'
AXES_ENABLED = env.bool("ACCOUNT_LOCKOUT_ENABLED", True)
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = timedelta(minutes=30)
AXES_LOCKOUT_PARAMETERS = ["ip_address"]
AXES_LOCKOUT_CALLABLE = "users.helpers.lockout_response"
