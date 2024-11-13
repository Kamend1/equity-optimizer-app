from django.db import models
from .utils import percentage_return_classifier


class StockDataManager(models.Manager):
    def calculate_daily_return(self, stock, date, adj_close):
        previous_day = self.filter(stock=stock, date__lt=date).order_by('-date').first()
        if previous_day:
            daily_return = ((adj_close - previous_day.adj_close) / previous_day.adj_close) * 100
        else:
            daily_return = 0
        return daily_return

    def calculate_trend(self, daily_return):
        return percentage_return_classifier(daily_return)


class StockManager(models.Manager):
    def last_adj_close(self):
        last_stock_data = self.historical_data.order_by('-date').first()
        return float(last_stock_data.adj_close) if last_stock_data else 0

    def get_last_adj_close_to_usd(self):
        last_adj_close_to_usd = self.historical_data.order_by('-date').first()
        return float(last_adj_close_to_usd)