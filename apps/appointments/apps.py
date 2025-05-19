from django.apps import AppConfig

class AppointmentsConfig(AppConfig):
            default_auto_field = 'django.db.models.BigAutoField'
            name = 'apps.appointments'

            def ready(self):
                # Import signals ở đây
                try:
                    import apps.appointments.signals # Hoặc from . import signals
                except ImportError:
                    pass
        