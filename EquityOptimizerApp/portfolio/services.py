from django.db import transaction
from django.utils import timezone
from EquityOptimizerApp.portfolio.models import Portfolio, PortfolioValueHistory, PortfolioStock
from EquityOptimizerApp.equity_optimizer.models import Stock, StockData
from datetime import timedelta


class PortfolioCreationService:
    @staticmethod
    @transaction.atomic
    def create_from_simulation(user, name, description, best_portfolio_data, initial_investment):
        portfolio = Portfolio.objects.create(user=user, name=name, description=description)
        total_value = 0

        for weight, stock_symbol in best_portfolio_data['Weights']:
            stock = Stock.objects.get(ticker=stock_symbol)
            stock_price = stock.last_adj_close()
            quantity = (initial_investment * float(weight) / 100) / stock_price
            total_value += quantity * stock_price

            PortfolioStock.objects.create(portfolio=portfolio, stock=stock, quantity=float(quantity))

        PortfolioValueHistory.objects.create(portfolio=portfolio, date=timezone.now().date(), value=total_value)
        return portfolio


class PortfolioValueService:
    @staticmethod
    def calculate_daily_value(portfolio):
        last_record = PortfolioValueHistory.objects.filter(portfolio=portfolio).order_by('-date').first()
        start_date = last_record.date + timedelta(days=1) if last_record else portfolio.created_at.date()
        end_date = timezone.now().date()
        stocks_quantities = {ps.stock_id: ps.quantity for ps in PortfolioStock.objects.filter(portfolio=portfolio)}

        current_date = start_date
        previous_value = last_record.value if last_record else None

        while current_date <= end_date:
            daily_value = 0
            all_prices_available = True

            for stock_id, quantity in stocks_quantities.items():
                try:
                    stock_data = StockData.objects.get(stock_id=stock_id, date=current_date)
                    daily_value += stock_data.adj_close_to_usd * quantity
                except StockData.DoesNotExist:
                    all_prices_available = False
                    break

            if all_prices_available and daily_value > 0:
                daily_return = ((daily_value - previous_value) / previous_value * 100) if previous_value else 0
                PortfolioValueHistory.objects.update_or_create(
                    portfolio=portfolio, date=current_date, defaults={
                        'value': daily_value,
                        'daily_return': daily_return,
                    }
                )
                previous_value = daily_value

            current_date += timedelta(days=1)

    @staticmethod
    def update_all_portfolios():
        portfolios = Portfolio.objects.all()
        for portfolio in portfolios:
            PortfolioValueService.calculate_daily_value(portfolio)
