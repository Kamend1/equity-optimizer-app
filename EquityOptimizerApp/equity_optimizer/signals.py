from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Stock
from EquityOptimizerApp.currencies.models import Currency


@receiver(pre_save, sender=Stock)
def ensure_currency_exists(sender, instance, **kwargs):
    if instance.currency_code and not Currency.objects.filter(code=instance.currency_code).exists():
        Currency.objects.create(
            code=instance.currency_code,
            name=instance.currency_code,
            symbol=instance.currency_code
        )
        print(f"Created new currency: {instance.currency_code}")
