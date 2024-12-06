from django.apps import AppConfig


class RegisterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'EquityOptimizerApp.accounts'

    def ready(self):
        import EquityOptimizerApp.accounts.signals
