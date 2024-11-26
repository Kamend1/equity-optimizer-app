from celery import shared_task
import logging
from EquityOptimizerApp.portfolio.services import PortfolioValueService

logger = logging.getLogger(__name__)

portfolio_value_service = PortfolioValueService()


@shared_task(bind=True, max_retries=5)
def update_portfolios(self):
    try:
        portfolio_value_service.update_all_portfolios()
        logger.info("Portfolios updated successfully.")
    except Exception as e:
        logger.error(f"Portfolios not updated: {e}")
        self.retry(exc=e, countdown=60)
