
"""
Configuración Django para AXI.
Configuración por ambientes: local, docker, production
"""

import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================================================
# CONFIGURACIÓN POR AMBIENTE (ESTRATEGIA SIMPLE)
# ============================================================================
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")

# settings.py mejorado
if ENVIRONMENT == "local":
    load_dotenv(".env.local")
elif ENVIRONMENT == "docker":
    load_dotenv(".env.docker") 
elif ENVIRONMENT == "gcp-local":         # ← NUEVO
    load_dotenv(".env.gcp-local")        # ← Testing GCP local
    print("☁️ GCP-LOCAL: Cargando .env.gcp-local")
else:
    print("🔵 PRODUCTION: Variables del sistema")

# ============================================================================
# CONFIGURACIÓN BASE (COMÚN A TODOS)
# ============================================================================
SECRET_KEY = os.getenv("SECRET_KEY", "dev-insecure-change-me")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
ALLOWED_HOSTS = ["*"]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'drf_spectacular',
    'apps.auth',
    'apps.datasets',
    'apps.analytics',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.datasets.middleware.StructuredLoggingMiddleware',
]

ROOT_URLCONF = 'axi.urls'
WSGI_APPLICATION = 'axi.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

# ============================================================================
# CONFIGURACIÓN POR AMBIENTE - BASE DE DATOS
# ============================================================================
DB_ENGINE = os.getenv("DB_ENGINE", "sqlite")

if DB_ENGINE == "postgres":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DB_NAME", "analytics"),
            "USER": os.getenv("DB_USER", "analytics"),
            "PASSWORD": os.getenv("DB_PASSWORD", "analytics"),
            "HOST": os.getenv("DB_HOST", "localhost"),
            "PORT": os.getenv("DB_PORT", 5432),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ============================================================================
# CONFIGURACIÓN POR AMBIENTE - ARCHIVOS ESTÁTICOS
# ============================================================================
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

if ENVIRONMENT == "local":
    # Local: sin compresión para desarrollo rápido
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
else:
    # Docker/Production: con compresión
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ============================================================================
# CONFIGURACIÓN POR AMBIENTE - ARCHIVOS MEDIA (UPLOADS)
# ============================================================================
USE_GCS = os.getenv("USE_GCS", "false").lower() == "true"

if USE_GCS:
    # PRODUCTION: Google Cloud Storage
    DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
    GS_BUCKET_NAME = os.getenv("GS_BUCKET_NAME", "analytics-api-files-prod")
    GS_DEFAULT_ACL = None  
    GS_QUERYSTRING_AUTH = True  
    GS_EXPIRATION = timedelta(seconds=300)  # 5 min para signed URLs
    MEDIA_URL = f"https://storage.googleapis.com/{GS_BUCKET_NAME}/"
    GS_CREDENTIALS = None  # Auto-detect en GCP
else:
    # LOCAL/DOCKER: Archivos locales
    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"

# ============================================================================
# CONFIGURACIÓN POR AMBIENTE - LOGGING
# ============================================================================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "[{levelname}] {asctime} {name}: {message}", "style": "{"},
        "verbose": {"format": "[{levelname}] {asctime} {name} {process:d} {thread:d}: {message}", "style": "{"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple" if ENVIRONMENT == "local" else "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": LOG_LEVEL,
    },
    "loggers": {
        "django.request": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        "django.db.backends": {
            "handlers": ["console"], 
            "level": "DEBUG" if ENVIRONMENT == "local" else "WARNING", 
            "propagate": False
        },
    },
}

# ============================================================================
# REST FRAMEWORK & JWT (CONFIGURACIÓN COMÚN)
# ============================================================================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "apps.datasets.errors.custom_exception_handler",
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=int(os.getenv("JWT_ACCESS_TOKEN_LIFETIME", 60))),
    'REFRESH_TOKEN_LIFETIME': timedelta(minutes=int(os.getenv("JWT_REFRESH_TOKEN_LIFETIME", 1440))),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Analytics API",
    "DESCRIPTION": "API para análisis de datos CSV",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "persistAuthorization": True,
        "displayOperationId": False,
    },
    "COMPONENT_SPLIT_REQUEST": True,  # Importante para file uploads
}

# ============================================================================
# CONFIGURACIÓN ESTÁNDAR DJANGO (NO CAMBIA POR AMBIENTE)
# ============================================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================================================
# CONFIGURACIÓN CELERY
# ============================================================================
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# ============================================================================
# DEBUG: MOSTRAR CONFIGURACIÓN ACTUAL
# ============================================================================
print(f"🎯 Ambiente: {ENVIRONMENT}")
DB_SOURCE = 'Docker' if os.getenv("DB_HOST") == "db" else 'Local'
print(f"🔧 Base de datos: {DB_ENGINE} {DB_SOURCE}")
print(f"📁 Storage: {'GCS' if USE_GCS else 'Local'}")
print(f"🐛 Debug: {DEBUG}")
