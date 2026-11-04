"""Django settings for the ARS Garments storefront."""
import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
import pymysql

# Django's MySQL backend imports the MySQLdb API; use PyMySQL's compatible shim.
pymysql.install_as_MySQLdb()

BASE_DIR = Path(__file__).resolve().parent.parent

# Read simple KEY=value settings from a local, git-ignored .env file.
env_file = BASE_DIR / ".env"
if env_file.exists():
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip().strip("\"'")
        if key.strip():
            os.environ.setdefault(key.strip(), value)

DEBUG = os.environ.get("DJANGO_DEBUG", "False").lower() == "true"
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "local-development-key-change-before-deployment")
if not DEBUG and (len(SECRET_KEY) < 50 or SECRET_KEY == "local-development-key-change-before-deployment"):
    raise ValueError("Set DJANGO_SECRET_KEY to a unique random value of at least 50 characters when DEBUG is False.")
ALLOWED_HOSTS = [host.strip() for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if host.strip()]
CSRF_TRUSTED_ORIGINS = [
    origin.strip() for origin in os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") if origin.strip()
]
vercel_host = os.environ.get("VERCEL_URL", "").strip()
if vercel_host:
    ALLOWED_HOSTS.append(vercel_host)
    CSRF_TRUSTED_ORIGINS.append(f"https://{vercel_host}")
DJANGO_TRUST_PROXY_CLIENT_IP = os.environ.get("DJANGO_TRUST_PROXY_CLIENT_IP", "False").lower() == "true"

INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "store.apps.StoreConfig",
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
ROOT_URLCONF = "ars_garments.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
        "store.context_processors.cart_summary",
    ]},
}]
WSGI_APPLICATION = "ars_garments.wsgi.application"
DB_MIGRATION_MODE = os.environ.get("DJANGO_DB_MIGRATION", "False").lower() == "true"
DATABASE_USER = os.environ.get(
    "MYSQL_MIGRATION_USER" if DB_MIGRATION_MODE else "MYSQL_USER",
    "ars_garments_migrator" if DB_MIGRATION_MODE else "ars_garments_app",
)
DATABASE_PASSWORD = os.environ.get(
    "MYSQL_MIGRATION_PASSWORD" if DB_MIGRATION_MODE else "MYSQL_PASSWORD", ""
)
if DB_MIGRATION_MODE and not DATABASE_PASSWORD:
    raise ImproperlyConfigured(
        "DJANGO_DB_MIGRATION=True requires MYSQL_MIGRATION_PASSWORD in .env or the environment."
    )
if not DEBUG and DATABASE_USER.lower() == "root":
    raise ImproperlyConfigured("Do not use MySQL root for the application. Configure a least-privilege MYSQL_USER.")
if not DEBUG and not DATABASE_PASSWORD:
    raise ImproperlyConfigured("Set the MySQL password for the configured application or migration user.")
DATABASES = {"default": {
    "ENGINE": "django.db.backends.mysql",
    "NAME": os.environ.get("MYSQL_DATABASE", "ars_garments"),
    "USER": DATABASE_USER,
    "PASSWORD": DATABASE_PASSWORD,
    "HOST": os.environ.get("MYSQL_HOST", "127.0.0.1"),
    "PORT": os.environ.get("MYSQL_PORT", "3306"),
    "OPTIONS": {"charset": "utf8mb4"},
}}
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LANGUAGE_CODE = "en-in"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = os.environ.get("DJANGO_SECURE_SSL_REDIRECT", str(not DEBUG)).lower() == "true"
if os.environ.get("DJANGO_TRUST_PROXY_SSL_HEADER", "False").lower() == "true":
    # Set only when the app is behind a trusted proxy that overwrites this header (Vercel does).
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = int(os.environ.get("DJANGO_SECURE_HSTS_SECONDS", "31536000" if not DEBUG else "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = os.environ.get("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", "False").lower() == "true"
SECURE_HSTS_PRELOAD = os.environ.get("DJANGO_SECURE_HSTS_PRELOAD", "False").lower() == "true"
