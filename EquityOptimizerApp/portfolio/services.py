from django.db.models import Sum, F
from django.db import transaction
from django.utils import timezone
from EquityOptimizerApp.portfolio.models import Portfolio, PortfolioValueHistory, PortfolioStock
from EquityOptimizerApp.equity_optimizer.models import Stock, StockData
from datetime import timedelta
from math import floor


def get_portfolio_sector_breakdown(self):
    sectors = self.portfolio_stocks.values('stock__sector').annotate(
        total_value=Sum(F('quantity') * F('stock__latest_price'))
    )
    return sectors


def get_portfolio_value_history(portfolio_id):
    return PortfolioValueHistory.objects.filter(portfolio_id=portfolio_id).order_by('date')


@transaction.atomic
def save_portfolio_from_simulation(user, name, description, best_portfolio_data, initial_investment):
    # Create the portfolio
    portfolio = Portfolio.objects.create(
        user=user,
        name=name,
        description=description,
    )

    # Calculate and save the stock quantities
    total_portfolio_value = 0
    for weight, stock_symbol in best_portfolio_data['Weights']:
        stock = Stock.objects.get(ticker=stock_symbol)
        stock_price = stock.last_adj_close()  # Assuming you have a method to get the current price
        quantity = floor((initial_investment * float(weight) / 100) // stock_price)
        total_portfolio_value += quantity * stock_price

        PortfolioStock.objects.create(
            portfolio=portfolio,
            stock=stock,
            quantity=int(quantity),
        )

    PortfolioValueHistory.objects.create(
        portfolio=portfolio,
        date=timezone.now().date(),
        value=total_portfolio_value
    )

    return portfolio


def calculate_daily_portfolio_value(portfolio):
    """
    Calculate and store daily portfolio values for a portfolio, starting from the next day
    after the last recorded date or the portfolio's creation date if no history exists.
    """
    last_value_record = PortfolioValueHistory.objects.filter(portfolio=portfolio).order_by('-date').first()
    start_date = last_value_record.date + timedelta(days=1) if last_value_record else portfolio.created_at.date()
    end_date = timezone.now().date()

    portfolio_stocks = PortfolioStock.objects.filter(portfolio=portfolio)
    stocks_quantities = {ps.stock_id: ps.quantity for ps in portfolio_stocks}

    current_date = start_date
    previous_day_value = last_value_record.value if last_value_record else None

    while current_date <= end_date:
        daily_value = 0
        all_prices_available = True

        for stock_id, quantity in stocks_quantities.items():
            try:
                stock_data = StockData.objects.get(stock_id=stock_id, date=current_date)
                daily_value += stock_data.adj_close * quantity
            except StockData.DoesNotExist:
                all_prices_available = False
                break

        if all_prices_available and daily_value > 0:
            daily_return = ((daily_value - previous_day_value) / previous_day_value * 100) if previous_day_value else 0

            PortfolioValueHistory.objects.update_or_create(
                portfolio=portfolio,
                date=current_date,
                defaults={'value': daily_value, 'daily_return': daily_return}
            )

            previous_day_value = daily_value

        current_date += timedelta(days=1)


def update_all_portfolios_daily_values():
    """
    Loop through all portfolios and calculate their daily values.
    """
    portfolios = Portfolio.objects.all()
    for portfolio in portfolios:
        calculate_daily_portfolio_value(portfolio)