import os
from django.core.exceptions import ImproperlyConfigured

env_setting = os.getenv("DJANGO_ENV", "local")
if env_setting == "production":
    from .production import *  # noqa
elif env_setting == "local":
    from .local import *  # noqa
else:
    raise ImproperlyConfigured("Unknown DJANGO_ENV={}".format(env_setting))
