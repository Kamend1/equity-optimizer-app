from django.db import models


class PortfolioManager(models.Manager):

    def calculate_value(self):
        total_value = 0
        for portfolio_stock in self.portfolio_stocks.all():
            stock_price = portfolio_stock.stock.get_latest_price()
            total_value += stock_price * portfolio_stock.quantity
        return total_value
