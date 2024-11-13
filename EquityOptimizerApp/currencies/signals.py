import pandas as pd
import yfinance as yf
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Currency, ExchangeRate


@receiver(post_save, sender=Currency)
def populate_exchange_rate(sender, instance, created, **kwargs):
    """
    Signal handler to populate ExchangeRate data when a new Currency instance is created.
    """
    if created:
        base_currency_code = "USD"
        target_currency_code = instance.code

        if target_currency_code == base_currency_code:
            return

        ticker = f"{base_currency_code}{target_currency_code}=X"

        print(f"Fetching exchange rate data for {ticker}...")

        try:
            data = yf.Ticker(ticker).history(start="2010-01-01")
            if data.empty:
                print(f"No data found for {ticker}.")
                return

            exchange_rate_objects = [
                ExchangeRate(
                    base_currency=Currency.objects.get(code=base_currency_code),
                    target_currency=instance,
                    date=pd.to_datetime(row.name).date(),
                    rate=row['Close']
                )
                for _, row in data.iterrows()
            ]

            ExchangeRate.objects.bulk_create(exchange_rate_objects, batch_size=1000)
            print(f"Successfully populated exchange rate data for {ticker}.")
        except Exception as e:
            print(f"Failed to fetch exchange rate data for {ticker}: {e}")
