from celery import chain, shared_task
from EquityOptimizerApp.currencies.tasks import update_currencies
from EquityOptimizerApp.equity_optimizer.tasks import update_stocks
from EquityOptimizerApp.portfolio.tasks import update_portfolios


@shared_task
def update_all_data():

    try:

        chain(
            update_currencies.s(),
            update_stocks.s(),
            update_portfolios.s()
        ).apply_async()
        print("All data updates scheduled sequentially.")
    except Exception as e:
        raise Exception(f"Failed to schedule updates: {str(e)}")
