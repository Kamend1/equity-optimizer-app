from django.db import models
from django.utils import timezone


class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=5, blank=True, null=True)

    def __str__(self):
        return f"{self.code} - {self.name}"


class ExchangeRate(models.Model):
    base_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='base_rates')
    target_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='target_rates')
    date = models.DateField(default=timezone.now)
    rate = models.FloatField()

    class Meta:
        unique_together = ('base_currency', 'target_currency', 'date')
        indexes = [
            models.Index(fields=['base_currency', 'target_currency', 'date']),
        ]

    def __str__(self):
        return f"1 {self.base_currency.code} = {self.rate} {self.target_currency.code} on {self.date}"
