from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models import Index
from django.contrib.auth.models import User
from .mixins import CreatedAtMixin, UpdatedAtMixin
from .managers import StockDataManager, StockManager, PortfolioManager


# Create your models here.
class Stock(CreatedAtMixin, UpdatedAtMixin):
    ticker = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    sector = models.CharField(max_length=100, blank=True, null=True)

    # Company Details
    market_cap = models.BigIntegerField(blank=True, null=True)
    enterprise_value = models.BigIntegerField(blank=True, null=True)
    trailing_pe = models.FloatField(blank=True, null=True)
    forward_pe = models.FloatField(blank=True, null=True)
    peg_ratio = models.FloatField(blank=True, null=True)
    price_to_book = models.FloatField(blank=True, null=True)
    profit_margin = models.FloatField(blank=True, null=True)
    operating_margin = models.FloatField(blank=True, null=True)

    # Financial Data
    revenue = models.BigIntegerField(blank=True, null=True)
    gross_profit = models.BigIntegerField(blank=True, null=True)
    ebitda = models.BigIntegerField(blank=True, null=True)
    net_income = models.BigIntegerField(blank=True, null=True)
    diluted_eps = models.FloatField(blank=True, null=True)

    # Balance Sheet Data
    total_cash = models.BigIntegerField(blank=True, null=True)
    total_debt = models.BigIntegerField(blank=True, null=True)
    total_assets = models.BigIntegerField(blank=True, null=True)
    total_liabilities = models.BigIntegerField(blank=True, null=True)

    # Dividend Data
    dividend_yield = models.FloatField(blank=True, null=True)
    dividend_rate = models.FloatField(blank=True, null=True)
    payout_ratio = models.FloatField(blank=True, null=True)

    # Stock Performance Data
    beta = models.FloatField(blank=True, null=True)
    fifty_two_week_high = models.FloatField(blank=True, null=True)
    fifty_two_week_low = models.FloatField(blank=True, null=True)
    average_daily_volume = models.BigIntegerField(blank=True, null=True)

    objects = StockManager()

    def last_adj_close(self):
        last_stock_data = self.historical_data.order_by('-date').first()
        return float(last_stock_data.adj_close) if last_stock_data else 0

    def __str__(self):
        return f"{self.ticker} - {self.name}"


class StockData(CreatedAtMixin, UpdatedAtMixin, models.Model):
    stock = models.ForeignKey(Stock, related_name='historical_data', on_delete=models.CASCADE)
    date = models.DateField()
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    adj_close = models.FloatField()
    volume = models.BigIntegerField()
    daily_return = models.FloatField(null=True, blank=True)
    trend = models.CharField(max_length=50, null=True, blank=True)

    objects = StockDataManager()

    def save(self, *args, **kwargs):
        self.daily_return = StockData.objects.calculate_daily_return(self.stock, self.date, self.adj_close)
        self.trend = StockData.objects.calculate_trend(self.daily_return)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.stock} on {self.date}"

    class Meta:
        unique_together = ('stock', 'date')
        indexes = [
            Index(fields=['stock', 'date']),  # Composite index on stock and date
        ]
