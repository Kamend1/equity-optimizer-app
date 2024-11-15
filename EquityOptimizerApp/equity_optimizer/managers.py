from django.db import models
from django.db.models import OuterRef, Subquery

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
    def get_last_adj_close(self):

        from .models import StockData

        latest_record = StockData.objects.filter(stock_id=OuterRef('id')).order_by('-date').values('adj_close')[:1]
        return Subquery(latest_record)

    def get_last_adj_close_to_usd(self):

        from .models import StockData

        latest_record = StockData.objects.filter(stock_id=OuterRef('id')).order_by('-date').values('adj_close_to_usd')[:1]
        return Subquery(latest_record)

    def annotate_with_latest_adj_close(self, queryset):
        queryset = queryset.annotate(
            latest_adj_close=self.get_last_adj_close(),
            latest_adj_close_to_usd=self.get_last_adj_close_to_usd()
        )
        return queryset
