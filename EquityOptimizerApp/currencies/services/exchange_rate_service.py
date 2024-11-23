import pandas as pd
from django.db import transaction
from pandas.tseries import offsets

from EquityOptimizerApp.currencies.models import Currency, ExchangeRate
from .yfinance_exchange_rate_fetcher import YFinanceExchangeRateFetcher


class ExchangeRateService:
    def __init__(self, fetcher=None):
        self.fetcher = fetcher or YFinanceExchangeRateFetcher()

    @staticmethod
    def get_exchange_rate(target_currency_code, date):
        """
        Fetch the exchange rate for the target currency to USD on a specific date.
        """
        try:

            exchange_rate = ExchangeRate.objects.filter(
                base_currency__code='USD',
                target_currency__code=target_currency_code,
                date=date
            ).first()

            if exchange_rate:
                return float(exchange_rate.rate)

            exchange_rate = ExchangeRate.objects.filter(
                base_currency__code='USD',
                target_currency__code=target_currency_code,
                date__lte=date
            ).order_by('-date').first()

            if exchange_rate:
                print(f"Using latest available exchange rate for {target_currency_code} on {exchange_rate.date}.")
                return float(exchange_rate.rate)

            if target_currency_code == 'USD':
                return 1.0

            raise ValueError(f"Exchange rate for {target_currency_code} on {date} is missing.")

        except Exception as e:
            print(f"Error fetching exchange rate for {target_currency_code} on {date}: {str(e)}")
            raise

    def update_exchange_rates(self, base_currency_code='USD', target_currency_code=None, start_date='2010-01-01'):
        print(f"Debug: Entered update_exchange_rates with target_currency_code={target_currency_code}")

        try:
            if not target_currency_code or target_currency_code == base_currency_code:
                print("Debug: Exiting early due to target_currency_code check")
                return

            try:
                target_currency = Currency.objects.get(code=target_currency_code)
                base_currency = Currency.objects.get(code=base_currency_code)
            except Currency.DoesNotExist as e:
                print(f"Error: Currency not found. {e}")
                return

            latest_record = ExchangeRate.objects.filter(
                base_currency=base_currency,
                target_currency=target_currency
            ).order_by('-date').first()

            if latest_record:
                start_date = max((latest_record.date - offsets.BDay(2)).date(), pd.to_datetime(start_date).date())
            else:
                start_date = pd.to_datetime(start_date).date()

            print(
                f"Updating exchange rates for {base_currency_code} to {target_currency_code} starting from {start_date}...")

            data = self.fetcher.fetch_exchange_rate_data(base_currency_code, target_currency_code, str(start_date))
            if data.empty:
                print(f"No historical data found for {base_currency_code} to {target_currency_code}.")
                return

            data.reset_index(inplace=True)

            existing_records_set = set(
                ExchangeRate.objects.filter(
                    base_currency=base_currency,
                    target_currency=target_currency
                ).values_list('target_currency_id', 'date')
            )
            update_exchange_rate_objects = []
            create_exchange_rate_objects = []

            for _, row in data.iterrows():
                date_value = pd.to_datetime(row['Date']).date()
                record_key = (target_currency.id, date_value)

                rate = row['Close']

                if record_key in existing_records_set:

                    existing_record = ExchangeRate.objects.get(
                        base_currency=base_currency,
                        target_currency=target_currency,
                        date=date_value
                    )

                    existing_record.rate = rate
                    update_exchange_rate_objects.append(existing_record)

                else:

                    new_record = ExchangeRate(
                        base_currency=base_currency,
                        target_currency=target_currency,
                        date=date_value,
                        rate=rate
                    )
                    create_exchange_rate_objects.append(new_record)

            print(f"Debug: Preparing to bulk update {len(update_exchange_rate_objects)} records.")
            print(f"Debug: Preparing to bulk create {len(create_exchange_rate_objects)} records.")

            with transaction.atomic():
                if update_exchange_rate_objects:
                    fields_to_update = ['base_currency', 'target_currency', 'date', 'rate']
                    try:
                        ExchangeRate.objects.bulk_update(update_exchange_rate_objects, fields=fields_to_update,
                                                         batch_size=1000)
                        print(f"Debug: Successfully updated {len(update_exchange_rate_objects)} records.")
                    except Exception as e:
                        print(f"Error during bulk_update: {e}")
                        raise

                if create_exchange_rate_objects:
                    try:
                        ExchangeRate.objects.bulk_create(create_exchange_rate_objects, batch_size=1000)
                        print(f"Debug: Successfully created {len(create_exchange_rate_objects)} records.")
                    except Exception as e:
                        print(f"Error during bulk_create: {e}")
                        raise

        except Exception as e:
            print(f"Unexpected error in update_exchange_rates: {e}")
            raise
