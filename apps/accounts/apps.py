from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'

    def ready(self):
        # Import signals ở đây
        try:
            import apps.accounts.signals # Hoặc from . import signals
        except ImportError:
            pass
