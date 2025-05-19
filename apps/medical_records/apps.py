from django.apps import AppConfig

class MedicalRecordsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.medical_records'

    def ready(self):
        # Import signals ở đây
        try:
            import apps.medical_records.signals # Hoặc from . import signals
        except ImportError:
            pass
