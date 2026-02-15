import os
from pathlib import Path

from dotenv import load_dotenv
from apps.reporting.ai_runtime import get_runtime_profile

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-only-secret-key")
DEBUG = os.getenv("DJANGO_DEBUG", "True") == "True"


def _build_allowed_hosts() -> list[str]:
    raw = os.getenv("DJANGO_ALLOWED_HOSTS", "").strip()
    default_hosts = ["localhost", "127.0.0.1", "0.0.0.0"]
    if not raw:
        hosts = default_hosts
    else:
        hosts = [h.strip() for h in raw.split(",") if h.strip()]
        if not hosts:
            hosts = default_hosts
    if DEBUG and "testserver" not in hosts:
        hosts.append("testserver")
    return hosts


ALLOWED_HOSTS = _build_allowed_hosts()

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_htmx",
    "apps.tenants",
    "apps.accounts",
    "apps.dashboard",
    "apps.reporting",
    "apps.meetings",
    "apps.tasks",
    "apps.presentations",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "office_copilot.middleware.TenantMiddleware",
]

ROOT_URLCONF = "office_copilot.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "office_copilot.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.getenv("DB_NAME", BASE_DIR / "db.sqlite3"),
        "USER": os.getenv("DB_USER", ""),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", ""),
        "PORT": os.getenv("DB_PORT", ""),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

AUTH_USER_MODEL = "accounts.User"

LOGIN_URL = "/auth/login/"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

OFFICE_CPU_TARGET = os.getenv("OFFICE_CPU_TARGET", "0.75")
OFFICE_EMBED_MODEL = os.getenv("OFFICE_EMBED_MODEL", "nltk-frequency")

# Initialize runtime profile early so thread controls are active before heavy processing.
RUNTIME_PROFILE = get_runtime_profile()
