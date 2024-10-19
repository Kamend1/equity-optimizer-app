from django.db.models import Sum, F
from django.db import transaction
from django.utils import timezone
from EquityOptimizerApp.portfolio.models import Portfolio, PortfolioValueHistory, PortfolioStock
from EquityOptimizerApp.equity_optimizer.models import Stock
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
