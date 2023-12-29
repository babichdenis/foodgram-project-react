import os
from dotenv import load_dotenv
from pathlib import Path

from django.core.management.utils import get_random_secret_key

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", get_random_secret_key())

DEBUG = os.getenv("DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")


INSTALLED_APPS = [
    "users.apps.UsersConfig",
    "api.apps.ApiConfig",
    "recipes.apps.RecipesConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "django_filters",
    "djoser",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "foodgram.urls"

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
            ],
        },
    },
]

WSGI_APPLICATION = "foodgram.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "foodgram"),
        "USER": os.getenv("POSTGRES_USER", "foodgram_user"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", ""),
        "PORT": os.getenv("DB_PORT", 5432),
    }
}


PASSWORD_VALIDATION_USER = (
    "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
)

PASSWORD_VALIDATION_MINIMUM = (
    "django.contrib.auth.password_validation.MinimumLengthValidator"
)
PASSWORD_VALIDATION_COMMON = (
    "django.contrib.auth.password_validation.CommonPasswordValidator"
)
PASSWORD_VALIDATION_NUMERIC = (
    "django.contrib.auth.password_validation.NumericPasswordValidator"
)

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": PASSWORD_VALIDATION_USER,
    },
    {
        "NAME": PASSWORD_VALIDATION_MINIMUM,
    },
    {
        "NAME": PASSWORD_VALIDATION_COMMON,
    },
    {
        "NAME": PASSWORD_VALIDATION_NUMERIC,
    },
]

LANGUAGE_CODE = "ru-RU"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


AUTH_USER_MODEL = "users.User"


STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PAGINATION_CLASS": "api.pagination.CustomPagination",
    "PAGE_SIZE": 6,
}

DJOSER = {
    "HIDE_USERS": False,
    "LOGIN_FIELD": "email",
    "SERIALIZERS": {
        "user_create": "api.serializers.UserCreateSerializer",
        "user": "api.serializers.UserGETSerializer",
        "current_user": "api.serializers.UserGETSerializer",
    },
    "PERMISSIONS": {
        'user': ['djoser.permissions.CurrentUserOrAdminOrReadOnly'],
        "user_list": ["rest_framework.permissions.AllowAny"],
    },
}
