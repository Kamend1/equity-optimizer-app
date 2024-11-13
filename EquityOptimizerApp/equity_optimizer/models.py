from django.db import models
from django.db.models import Index
from django.contrib.auth.models import User
from EquityOptimizerApp.mixins import CreatedAtMixin, UpdatedAtMixin
from .managers import StockDataManager, StockManager


# Create your models here.
class Stock(models.Model):
    ticker = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    sector = models.CharField(max_length=100, blank=True, null=True)
    industry = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    logo_url = models.URLField(blank=True, null=True)
    delisted = models.BooleanField(default=False)
    currency_code = models.CharField(max_length=3, default='USD', blank=False, null=False)

    # Market Data
    market_cap = models.BigIntegerField(blank=True, null=True)
    enterprise_value = models.BigIntegerField(blank=True, null=True)
    trailing_pe = models.FloatField(blank=True, null=True)
    forward_pe = models.FloatField(blank=True, null=True)
    peg_ratio = models.FloatField(blank=True, null=True)
    price_to_book = models.FloatField(blank=True, null=True)
    beta = models.FloatField(blank=True, null=True)

    # Valuation Metrics
    trailing_eps = models.FloatField(blank=True, null=True)
    forward_eps = models.FloatField(blank=True, null=True)
    book_value = models.FloatField(blank=True, null=True)
    fifty_two_week_high = models.FloatField(blank=True, null=True)
    fifty_two_week_low = models.FloatField(blank=True, null=True)
    fifty_day_average = models.FloatField(blank=True, null=True)

    # Financial Data
    revenue = models.BigIntegerField(blank=True, null=True)
    gross_profit = models.BigIntegerField(blank=True, null=True)
    ebitda = models.BigIntegerField(blank=True, null=True)
    net_income = models.BigIntegerField(blank=True, null=True)
    diluted_eps = models.FloatField(blank=True, null=True)
    profit_margin = models.FloatField(blank=True, null=True)  # Added back
    operating_margin = models.FloatField(blank=True, null=True)  # Added back

    # Balance Sheet Data
    total_cash = models.BigIntegerField(blank=True, null=True)
    total_debt = models.BigIntegerField(blank=True, null=True)
    total_assets = models.BigIntegerField(blank=True, null=True)
    total_liabilities = models.BigIntegerField(blank=True, null=True)

    # Dividend Data
    dividend_yield = models.FloatField(blank=True, null=True)
    dividend_rate = models.FloatField(blank=True, null=True)
    payout_ratio = models.FloatField(blank=True, null=True)
    ex_dividend_date = models.DateField(blank=True, null=True)
    last_dividend_date = models.DateField(blank=True, null=True)

    # Company Profile
    address1 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    full_time_employees = models.IntegerField(blank=True, null=True)
    long_business_summary = models.TextField(blank=True, null=True)

    # ESG (Sustainability) Data
    esg_scores = models.JSONField(blank=True, null=True)

    # Analyst Recommendations
    recommendations = models.JSONField(blank=True, null=True)

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
    adj_close_to_usd = models.FloatField(blank=True, null=True)

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
            Index(fields=['stock', 'date']),
        ]
