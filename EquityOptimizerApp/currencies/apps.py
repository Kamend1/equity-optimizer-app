from django.apps import AppConfig


class CurrenciesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'EquityOptimizerApp.currencies'

    def ready(self):
        import EquityOptimizerApp.currencies.signals
