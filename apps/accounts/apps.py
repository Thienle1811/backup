from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = "apps.accounts"            # Python import path
    label = "accounts"                # what Django will call it
    default_auto_field = "django.db.models.BigAutoField"
