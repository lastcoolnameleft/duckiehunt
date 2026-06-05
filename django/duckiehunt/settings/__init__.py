import os
from pathlib import Path

import flickr_api
import sentry_sdk
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv


DJANGO_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = DJANGO_DIR.parent
TEST_RECAPTCHA_PUBLIC_KEY = "6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI"
TEST_RECAPTCHA_PRIVATE_KEY = "6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe"

load_dotenv(PROJECT_ROOT / ".env")

_env_file = os.environ.get("ENV_FILE")
if _env_file:
    env_file_path = Path(_env_file)
    if not env_file_path.is_absolute():
        env_file_path = PROJECT_ROOT / env_file_path
    load_dotenv(env_file_path)


def _get_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}



def _get_list(name, default=""):
    value = os.environ.get(name, default)
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]



def _resolve_path(value):
    path = Path(value)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path



def _resolve_flickr_auth_file(value):
    path = Path(value)
    if path.is_absolute():
        return path

    project_path = PROJECT_ROOT / path
    if project_path.exists():
        return project_path

    return DJANGO_DIR / path



def _default_base_url():
    return "http://localhost:8042" if DEBUG else "https://duckiehunt.com"


_SECRET_KEY_INSECURE = "django-insecure-duckiehunt-local-dev-secret-key"
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")

DEBUG = _get_bool("DJANGO_DEBUG", default=True)

if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = _SECRET_KEY_INSECURE
    else:
        raise ImproperlyConfigured(
            "DJANGO_SECRET_KEY environment variable is required when DEBUG=False"
        )
BASE_URL = os.environ.get("DJANGO_BASE_URL", _default_base_url())
ALLOWED_HOSTS = _get_list(
    "DJANGO_ALLOWED_HOSTS",
    "localhost,127.0.0.1,0.0.0.0,duckiehunt.localhost",
)
CSRF_TRUSTED_ORIGINS = _get_list("DJANGO_CSRF_TRUSTED_ORIGINS", BASE_URL)

DB_DIR = _resolve_path(os.environ.get("DJANGO_DB_DIR", str(DJANGO_DIR / "data")))
DATABASE_NAME = str(DB_DIR / "duckiehunt.db")

UPLOAD_PATH = str(_resolve_path(os.environ.get("DJANGO_UPLOAD_DIR", str(DJANGO_DIR / "uploads"))))

# Media files (user-uploaded photos served locally until provider upload completes)
MEDIA_URL = '/media/'
MEDIA_ROOT = UPLOAD_PATH

SETTINGS_DIR = _resolve_path(os.environ.get("DJANGO_SETTINGS_DIR", str(DJANGO_DIR / "duckiehunt" / "settings")))

INSTALLED_APPS = [
    "duck.apps.DuckConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.humanize",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "social_django",
    "django_recaptcha",
    "django_q",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "social_django.middleware.SocialAuthExceptionMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

ROOT_URLCONF = "duckiehunt.urls"

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
                "duck.context_processors.google_maps_api_key",
            ],
        },
    },
]

WSGI_APPLICATION = "duckiehunt.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": DATABASE_NAME,
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
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

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = str(DJANGO_DIR / "staticfiles")
Path(STATIC_ROOT).mkdir(parents=True, exist_ok=True)

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "social_core.backends.google.GoogleOAuth2",
    "social_core.backends.facebook.FacebookOAuth2",
)

LOGIN_URL = "login"
LOGOUT_URL = "logout"
LOGIN_REDIRECT_URL = "mark"

SOCIAL_AUTH_FACEBOOK_KEY = os.environ.get("SOCIAL_AUTH_FACEBOOK_KEY", "")
SOCIAL_AUTH_FACEBOOK_SECRET = os.environ.get("SOCIAL_AUTH_FACEBOOK_SECRET", "")
SOCIAL_AUTH_FACEBOOK_SCOPE = ["email"]
SOCIAL_AUTH_FACEBOOK_API_VERSION = "2.11"

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get("SOCIAL_AUTH_GOOGLE_OAUTH2_KEY", "")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get("SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET", "")
SOCIAL_AUTH_REDIRECT_IS_HTTPS = BASE_URL.startswith("https://")

SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY", "")
if SENDGRID_API_KEY:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = "smtp.sendgrid.net"
    EMAIL_HOST_USER = "apikey"
    EMAIL_HOST_PASSWORD = SENDGRID_API_KEY
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    EMAIL_HOST = ""
    EMAIL_HOST_USER = ""
    EMAIL_HOST_PASSWORD = ""
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True

EMAIL_FROM = os.environ.get("DJANGO_EMAIL_FROM", "noreply@localhost")
EMAIL_TO = _get_list("DJANGO_EMAIL_TO", "")
DEFAULT_FROM_EMAIL = EMAIL_FROM
SERVER_EMAIL = EMAIL_FROM
ADMINS = [("Duckiehunt Admin", email) for email in EMAIL_TO]

RECAPTCHA_PUBLIC_KEY = os.environ.get("RECAPTCHA_PUBLIC_KEY", TEST_RECAPTCHA_PUBLIC_KEY)
RECAPTCHA_PRIVATE_KEY = os.environ.get("RECAPTCHA_PRIVATE_KEY", TEST_RECAPTCHA_PRIVATE_KEY)
SILENCED_SYSTEM_CHECKS = []
if (
    RECAPTCHA_PUBLIC_KEY == TEST_RECAPTCHA_PUBLIC_KEY
    and RECAPTCHA_PRIVATE_KEY == TEST_RECAPTCHA_PRIVATE_KEY
):
    SILENCED_SYSTEM_CHECKS.append("django_recaptcha.recaptcha_test_key_error")

GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "")

FLICKR_API_KEY = os.environ.get("FLICKR_API_KEY", "")
FLICKR_API_SECRET = os.environ.get("FLICKR_API_SECRET", "")
FLICKR_AUTH_FILE = os.environ.get("FLICKR_AUTH_FILE", str(SETTINGS_DIR / "flickr.auth"))
if FLICKR_AUTH_FILE:
    FLICKR_AUTH_FILE = str(_resolve_flickr_auth_file(FLICKR_AUTH_FILE))
FLICKR_PHOTO_IS_PUBLIC = "1" if _get_bool("FLICKR_PHOTO_IS_PUBLIC", default=False) else "0"
if FLICKR_API_KEY and FLICKR_API_SECRET:
    flickr_api.set_keys(api_key=FLICKR_API_KEY, api_secret=FLICKR_API_SECRET)
    if FLICKR_AUTH_FILE:
        flickr_api.set_auth_handler(FLICKR_AUTH_FILE)

GIT_SHA = os.environ.get("GIT_SHA", "unknown")
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Social media sharing (see duck/social.py)
FB_PAGE_ID = os.environ.get("FB_PAGE_ID", "")
FB_PAGE_ACCESS_TOKEN = os.environ.get("FB_PAGE_ACCESS_TOKEN", "")
IG_USER_ID = os.environ.get("IG_USER_ID", "")
IG_ACCESS_TOKEN = os.environ.get("IG_ACCESS_TOKEN", "")
LI_ACCESS_TOKEN = os.environ.get("LI_ACCESS_TOKEN", "")
LI_AUTHOR_URN = os.environ.get("LI_AUTHOR_URN", "")
LI_PERSON_URN = os.environ.get("LI_PERSON_URN", "")
LI_ORGANIZATION_URN = os.environ.get("LI_ORGANIZATION_URN", "")
LI_API_VERSION = os.environ.get("LI_API_VERSION", "")

# Django-Q2 background task queue (uses ORM/SQLite as broker)
Q_CLUSTER = {
    "name": "duckiehunt",
    "workers": 2,
    "timeout": 120,
    "retry": 180,
    "queue_limit": 50,
    "bulk": 10,
    "orm": "default",
    "sync": _get_bool("DJANGO_Q_SYNC", default=False),  # True = run tasks synchronously (for testing)
}

SENTRY_DSN = os.environ.get("SENTRY_DSN", "")
SENTRY_ENVIRONMENT = os.environ.get("SENTRY_ENVIRONMENT", "development")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=SENTRY_ENVIRONMENT,
        release=GIT_SHA,
        traces_sample_rate=0.1,
        send_default_pii=False,
    )

# Security hardening for production
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = True
    CSRF_COOKIE_SAMESITE = "Lax"
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}
