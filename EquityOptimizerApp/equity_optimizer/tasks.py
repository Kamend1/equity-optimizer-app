from celery import shared_task
import logging
from EquityOptimizerApp.equity_optimizer.services import YFinanceFetcher, StockUpdateService

logger = logging.getLogger(__name__)

fetcher = YFinanceFetcher()
stock_update_service = StockUpdateService()


@shared_task(bind=True, max_retries=5)
def update_stocks(self):
    try:
        stock_update_service.update_stock_data()
        logger.info('Stock data updated successfully!')
    except Exception as e:
        logger.error(f'Failed to update stock data. Retrying... Error: {str(e)}')
        self.retry(exc=e, countdown=60)
