"""Django settings for the Gainesville Utility App."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-not-for-production")

DEBUG = os.environ.get("DJANGO_DEBUG", "false").lower() == "true"

ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",")
    if h.strip()
]

CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",")
    if o.strip()
]

INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "Utility.apps.UtilityConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "WebApp.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
            ],
        },
    },
]

WSGI_APPLICATION = "WebApp.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.environ.get("DJANGO_DB_PATH", str(BASE_DIR / "data" / "utility.sqlite3")),
        "OPTIONS": {"init_command": "PRAGMA query_only = ON;"},
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/New_York"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static" / "static_root"
STATICFILES_DIRS = [BASE_DIR / "static" / "static_dirs"]
_staticfiles_backend = (
    "django.contrib.staticfiles.storage.StaticFilesStorage"
    if DEBUG
    # See WebApp/storage.py for why we subclass instead of using WhiteNoise's
    # stock storage directly.
    else "WebApp.storage.TolerantCompressedManifestStaticFilesStorage"
)

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": _staticfiles_backend,
    },
}

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
