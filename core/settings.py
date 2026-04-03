"""
Django settings for core project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# ============================================================
# 🔐 .env FILE LOAD (SABSE PEHLE — EK BAAR)
# ============================================================
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# 🔑 SECURITY SETTINGS
# ============================================================
# ✅ FIX: SECRET_KEY ab .env se aayega — hardcoded nahi
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-fallback-key-CHANGE-THIS-IN-PRODUCTION'
)

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*']  # Production mein specific domains likho

# ✅ Master Admin Credentials (.env se)
MASTER_ADMIN_USER = os.environ.get('MASTER_ADMIN_USER', 'admin')
MASTER_ADMIN_PASS = os.environ.get('MASTER_ADMIN_PASS', '')

# Ngrok & Local Development ke liye CSRF trusted origins
CSRF_TRUSTED_ORIGINS = [
    'https://*.ngrok-free.app',
    'https://*.ngrok.io',
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    'http://127.0.0.1:8080',
    'http://localhost:8080',
]

CORS_ALLOW_ALL_ORIGINS = True


# ============================================================
# 📦 INSTALLED APPS
# ============================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
   # ✅ FIX: INSTALLED_APPS mein add kiya
    'rest_framework',
    'drf_yasg',

    # Your apps
    'verifier',
]


# ============================================================
# ⚙️ MIDDLEWARE (✅ FIX: Duplicate list hata di, ek clean list)
# ============================================================
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',         # ✅ MUST be at the TOP
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ============================================================
# 🌐 URL & TEMPLATES
# ============================================================
ROOT_URLCONF = 'core.urls'

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

WSGI_APPLICATION = 'core.wsgi.application'


# ============================================================
# 🗄️ DATABASE
# ============================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ============================================================
# 🔒 PASSWORD VALIDATORS
# ============================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ============================================================
# 🌍 INTERNATIONALIZATION
# ============================================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'Asia/Karachi'
USE_I18N      = True
USE_TZ        = False  # False rakha hai taake Pakistan time seedha kaam kare


# ============================================================
# 📁 STATIC & MEDIA FILES
# ============================================================
STATIC_URL = '/static/'
MEDIA_URL  = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# ============================================================
# 📩 EMAIL CONFIGURATION (.env se secure)
# ============================================================
EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST          = 'smtp.gmail.com'
EMAIL_PORT          = 587
EMAIL_USE_TLS       = True
EMAIL_HOST_USER     = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
ADMIN_ALERT_EMAIL   = os.environ.get('ADMIN_ALERT_EMAIL', '')


# ============================================================
# 🚀 DJANGO REST FRAMEWORK
# ============================================================
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}


# ============================================================
# 📖 SWAGGER (drf-yasg) SETTINGS
# ============================================================
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {},
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
    'SUPPORTED_SUBMIT_METHODS': ['get', 'post', 'put', 'patch', 'delete'],
    'OPERATIONS_SORTER': 'alpha',   # Endpoints alphabetically sort honge
    'TAGS_SORTER': 'alpha',
    'DOC_EXPANSION': 'list',        # Swagger mein groups closed rakho by default
    'DEFAULT_MODEL_RENDERING': 'example',
}

# ============================================================
# 🍪 SESSION SETTINGS
# ============================================================
SESSION_ENGINE         = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE     = 86400   # 24 hours
SESSION_SAVE_EVERY_REQUEST = True