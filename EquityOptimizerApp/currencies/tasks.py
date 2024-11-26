from celery import shared_task
import logging

from EquityOptimizerApp.currencies.models import Currency
from EquityOptimizerApp.currencies.services.exchange_rate_service import ExchangeRateService
from EquityOptimizerApp.currencies.services.yfinance_exchange_rate_fetcher import YFinanceExchangeRateFetcher

logger = logging.getLogger(__name__)

fetcher = YFinanceExchangeRateFetcher()
exchange_rate_service = ExchangeRateService(fetcher)


@shared_task(bind=True, max_retries=5)
def update_currencies(self):

    try:
        currencies = Currency.objects.exclude(code='USD')
        if not currencies.exists():
            logger.info("No currencies to update.")
            return "No currencies to update."

        for currency in currencies:
            exchange_rate_service.update_exchange_rates(target_currency_code=currency.code)
            logger.info(f"Exchange rates updated for {currency.code}")

        return "Currencies updated successfully."
    except Exception as e:
        logger.error(f"Error updating currencies: {e}", exc_info=True)
        raise self.retry(exc=e, countdown=60)
