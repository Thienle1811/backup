from .base import *
import os
from pathlib import Path

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.railway.app',
    'django-server-production-2d8a.up.railway.app',
    'xn--ykhoaungbucnth-jtd8uv287bx0a.com.vn'
]

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('PGDATABASE'),
        'USER': os.getenv('PGUSER'),
        'PASSWORD': os.getenv('PGPASSWORD'),
        'HOST': os.getenv('PGHOST'),
        'PORT': os.getenv('PGPORT', '5432'),
    }
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = '/tmp/staticfiles'
STATICFILES_DIRS = [
    str(BASE_DIR / 'static'),
]

# Make sure staticfiles app is included
if 'django.contrib.staticfiles' not in INSTALLED_APPS:
    INSTALLED_APPS += ['django.contrib.staticfiles']

# Static files finders
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# WhiteNoise configuration (add whitenoise to middleware if not already there)
if 'whitenoise.middleware.WhiteNoiseMiddleware' not in MIDDLEWARE:
    # Insert after SecurityMiddleware
    security_index = MIDDLEWARE.index('django.middleware.security.SecurityMiddleware')
    MIDDLEWARE.insert(security_index + 1, 'whitenoise.middleware.WhiteNoiseMiddleware')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_MANIFEST_STRICT = False
WHITENOISE_USE_FINDERS = True

# Security Settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = str(BASE_DIR / 'media')
