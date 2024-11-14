from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Currency
from .services.exchange_rate_service import ExchangeRateService


@receiver(post_save, sender=Currency)
def populate_exchange_rate(sender, instance, created, **kwargs):
    """
    Signal handler to populate ExchangeRate data when a new Currency instance is created.
    """
    if created:
        if created:
            service = ExchangeRateService()
            service.update_exchange_rates(target_currency_code=instance.code)
