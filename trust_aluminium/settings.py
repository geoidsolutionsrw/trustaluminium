"""
Django settings for trust_aluminium project.

Updated for production deployment on Railway.
Local development still works with your existing MySQL setup.
"""

from pathlib import Path
import os
import pymysql
import dj_database_url
pymysql.install_as_MySQLdb()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Core security settings  (now read from environment variables)
# ---------------------------------------------------------------------------

# SECURITY: set a NEW, strong SECRET_KEY in Railway's Variables tab.
# Generate one with: python -c "import secrets; print(secrets.token_urlsafe(50))"
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-local-dev-only-CHANGE-ME",   # used only for local dev
)

# DEBUG is False in production. Set DEBUG=True in your LOCAL .env for development.
DEBUG = os.environ.get("DEBUG", "False") == "True"

# Hosts allowed to serve this app.
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# Railway injects this automatically with your service's public URL.
RAILWAY_DOMAIN = os.environ.get("RAILWAY_PUBLIC_DOMAIN")
if RAILWAY_DOMAIN:
    ALLOWED_HOSTS.append(RAILWAY_DOMAIN)

# Your custom domain (harmless to keep even before it's pointed at Railway).
ALLOWED_HOSTS += ["trustaluminium.rw", "www.trustaluminium.rw"]

# Required by Django for secure POST/CSRF across HTTPS domains.
CSRF_TRUSTED_ORIGINS = [
    "https://*.up.railway.app",
    "https://trustaluminium.rw",
    "https://www.trustaluminium.rw",
]


# ---------------------------------------------------------------------------
# Application definition
# ---------------------------------------------------------------------------

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'dash.apps.DashConfig',
    'authentication.apps.AuthenticationConfig',
    'sale.apps.SaleConfig',
    'product.apps.ProductConfig',
    'quotation.apps.QuotationConfig',
    'django.contrib.humanize',
    'django_extensions',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',   # serves static files (replaces Nginx)
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'trust_aluminium.middleware.CustomSessionMiddleware',
]

ROOT_URLCONF = 'trust_aluminium.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'trust_aluminium.wsgi.application'


# ---------------------------------------------------------------------------
# Database
# Local dev uses your existing MySQL. On Railway, add a MySQL database and it
# provides DATABASE_URL automatically (keep MySQL so your migrations match).
# ---------------------------------------------------------------------------

DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    # Production (Railway)
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
        )
    }
    # Preserve MySQL-specific options when on MySQL
    if DATABASES["default"].get("ENGINE") == "django.db.backends.mysql":
        DATABASES["default"]["OPTIONS"] = {
            "sql_mode": "STRICT_TRANS_TABLES",
            "charset": "utf8mb4",
        }
else:
    # Local development (your existing setup)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'trustaluminium_test',
            'HOST': 'localhost',
            'PORT': '3306',
            'USER': 'root',
            'PASSWORD': 'admin',
            'OPTIONS': {
                'sql_mode': 'STRICT_TRANS_TABLES',
                'charset': 'utf8mb4',
            },
        }
    }


# ---------------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# ---------------------------------------------------------------------------
# Static files (CSS, JavaScript, Images) — served by WhiteNoise in production
# ---------------------------------------------------------------------------

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]   # your source folder
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')     # collectstatic target

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = '/home'
LOGOUT_REDIRECT_URL = '/login'


# ---------------------------------------------------------------------------
# Email (read credentials from environment — never hard-code)
# IMPORTANT: revoke the old Gmail app password and set a new one in Railway.
# ---------------------------------------------------------------------------

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_SSL = False


# ---------------------------------------------------------------------------
# File uploads (media)
# NOTE: Railway's filesystem is EPHEMERAL — uploaded files are wiped on every
# redeploy. Attach a Railway Volume and set MEDIA_ROOT to its mount path
# (e.g. /data/media) so uploads survive, or use object storage (S3/Cloudinary).
# ---------------------------------------------------------------------------

MEDIA_URL = '/media/'
MEDIA_ROOT = os.environ.get("MEDIA_ROOT", BASE_DIR / 'media')


# ---------------------------------------------------------------------------
# Cache & sessions
# ---------------------------------------------------------------------------

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

ADMIN_USER_ID = 1
LOGIN_URL = 'home'
SESSION_COOKIE_AGE = 18000
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = False


# ---------------------------------------------------------------------------
# Production HTTPS hardening (active only when DEBUG is False)
# ---------------------------------------------------------------------------

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True