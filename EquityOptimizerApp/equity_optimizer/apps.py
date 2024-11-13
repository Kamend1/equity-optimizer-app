from django.apps import AppConfig


class EquityOptimizierConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'EquityOptimizerApp.equity_optimizer'

    def ready(self):
        import EquityOptimizerApp.equity_optimizer.signals