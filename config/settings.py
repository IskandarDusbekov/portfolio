"""
Django settings for config project.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def load_env(env_path):
    """Minimal .env loader (no external dependency, works on cPanel)."""
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        # Don't override variables already set in the real environment
        os.environ.setdefault(key, value)


load_env(BASE_DIR / ".env")

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-dev-only-change-me")
DEBUG = os.getenv("DJANGO_DEBUG", "True").lower() == "true"

ALLOWED_HOSTS = [host.strip() for host in os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if host.strip()]

# Django admin manzili — env orqali maxfiy qilish mumkin (masalan "boshqaruv-x7k/").
# Botlar standart "/admin/" ni skan qiladi, shuning uchun productionda o'zgartiring.
ADMIN_URL = os.getenv("DJANGO_ADMIN_URL", "admin/").strip().lstrip("/")
if ADMIN_URL and not ADMIN_URL.endswith("/"):
    ADMIN_URL += "/"

# Custom boshqaruv paneli manzili — env orqali maxfiy qilish mumkin.
PANEL_URL = os.getenv("DJANGO_PANEL_URL", "panel/").strip().lstrip("/")
if PANEL_URL and not PANEL_URL.endswith("/"):
    PANEL_URL += "/"
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]

INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "axes",
    "apps.main",
    "apps.blog",
    "apps.panel",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "apps.main.middleware.SiteLanguageMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.main.middleware.VisitTrackingMiddleware",
    # AxesMiddleware eng oxirida turishi shart
    "axes.middleware.AxesMiddleware",
]

# --- Brute-force himoyasi (django-axes) ---
AUTHENTICATION_BACKENDS = [
    # AxesStandaloneBackend eng birinchi bo'lishi shart
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# Necha marta xato urinishdan keyin blok qilinadi
AXES_FAILURE_LIMIT = int(os.getenv("DJANGO_AXES_FAILURE_LIMIT", "5"))
# Blok necha soatdan keyin ochiladi
AXES_COOLOFF_TIME = int(os.getenv("DJANGO_AXES_COOLOFF_HOURS", "1"))
# Blok username + IP kombinatsiyasi bo'yicha hisoblanadi
AXES_LOCKOUT_PARAMETERS = [["username", "ip_address"]]
# Muvaffaqiyatli kirishda hisoblagich tozalanadi
AXES_RESET_ON_SUCCESS = True
# Bloklanganda ko'rsatiladigan chiroyli sahifa
AXES_LOCKOUT_TEMPLATE = "panel/lockout.html"
# Blok javobining HTTP status kodi
AXES_HTTP_RESPONSE_CODE = 429

ROOT_URLCONF = "config.urls"

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
                "apps.main.context_processors.site_identity",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Tashkent"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "portfolio-cache",
    }
}

SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
X_FRAME_OPTIONS = "DENY"

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = True

JAZZMIN_SETTINGS = {
    "site_title": "Portfolio Admin",
    "site_header": "Portfolio Admin",
    "site_brand": "Portfolio",
    "site_logo_classes": "img-circle",
    "welcome_sign": "Portfolio boshqaruv paneli",
    "copyright": "Portfolio",
    "topmenu_links": [
        {"name": "Website", "url": "/", "new_window": True},
        {"model": "main.profile"},
        {"model": "blog.blogpost"},
        {"model": "main.contactmessage"},
    ],
    "icons": {
        "main.profile": "fas fa-id-card",
        "main.project": "fas fa-code-branch",
        "main.skill": "fas fa-tools",
        "main.sociallink": "fas fa-share-alt",
        "main.contactmessage": "fas fa-envelope",
        "blog.blogcategory": "fas fa-tags",
        "blog.blogpost": "fas fa-blog",
        "auth": "fas fa-users-cog",
    },
    "navigation_expanded": True,
    "show_sidebar": True,
    "changeform_format": "horizontal_tabs",
}

JAZZMIN_UI_TWEAKS = {
    "theme": "flatly",
    "dark_mode_theme": "darkly",
    "navbar": "navbar-primary navbar-dark",
    "accent": "accent-primary",
    "sidebar": "sidebar-dark-primary",
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "django_file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "django.log",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "standard",
        },
        "error_file": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "errors.log",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "standard",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "django_file", "error_file"],
            "level": "INFO",
            "propagate": True,
        },
        "django.request": {
            "handlers": ["error_file", "django_file"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.server": {
            "handlers": ["console", "django_file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
