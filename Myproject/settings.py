"""
Django settings for Myproject project.
"""

import os
import dj_database_url
from pathlib import Path
from dotenv import load_dotenv

# ================= BASE DIR =================

BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(BASE_DIR / '.env')

# ================= SECURITY =================

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-me')

DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = [host.strip() for host in os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',') if host.strip()]

# ================= AUTH USER =================

AUTH_USER_MODEL = 'users.PersonUser'

# ================= INSTALLED APPS =================

INSTALLED_APPS = [

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # Custom Apps
    'store',
    'admin_dashboard',
    'users',
    'payment',
    'user_dashboard',
]

# ================= MIDDLEWARE =================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',

    'django.middleware.common.CommonMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',

    'django.contrib.messages.middleware.MessageMiddleware',

    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ================= URLS =================

ROOT_URLCONF = 'Myproject.urls'

# ================= TEMPLATES =================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        'DIRS': [BASE_DIR / 'templates'],

        'APP_DIRS': True,

        'OPTIONS': {
            'context_processors': [

                'django.template.context_processors.request',

                'django.contrib.auth.context_processors.auth',

                'django.contrib.messages.context_processors.messages',

                'admin_dashboard.context_processors.notification_count',

                'store.context_processors.cart_count',
            ],
        },
    },
]

# ================= WSGI =================

WSGI_APPLICATION = 'Myproject.wsgi.application'

# ================= DATABASE =================

DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600,
    )
}

# ================= PASSWORD VALIDATION =================

AUTH_PASSWORD_VALIDATORS = [

    {
        'NAME':
            'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },

    {
        'NAME':
            'django.contrib.auth.password_validation.MinimumLengthValidator',
    },

    {
        'NAME':
            'django.contrib.auth.password_validation.CommonPasswordValidator',
    },

    {
        'NAME':
            'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ================= INTERNATIONALIZATION =================

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# ================= STATIC FILES =================

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'

# ================= MEDIA FILES =================

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'

# ================= EMAIL =================

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ================= PAYMENT =================

SANDBOX = True

MERCHANT = os.getenv('MERCHANT', '')
