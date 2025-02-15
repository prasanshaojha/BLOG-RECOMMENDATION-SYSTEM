from django.apps import AppConfig

class VaultappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'vaultapp'

    def ready(self):
        import vaultapp.signals  # Import the signals to ensure they are registered
