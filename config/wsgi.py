"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

# Set the settings module based on environment
if os.getenv('DJANGO_ENV') == 'production':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

application = get_wsgi_application()
