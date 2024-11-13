from django.core.validators import MinLengthValidator
from django.db import models
from django.utils import timezone
from EquityOptimizerApp.mixins import CreatedAtMixin, UpdatedAtMixin
from EquityOptimizerApp.portfolio.managers import PortfolioManager
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from EquityOptimizerApp.equity_optimizer.models import Stock


# Create your models here.
class Portfolio(CreatedAtMixin, UpdatedAtMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolios')
    name = models.CharField(max_length=100, validators=[MinLengthValidator(2)])
    description = models.TextField(blank=True, null=True)
    stocks = models.ManyToManyField('equity_optimizer.Stock', through='PortfolioStock', related_name='portfolios')
    public = models.BooleanField(default=False, null=True)

    objects = PortfolioManager()

    def clean(self):
        if self.pk:  # Only check if the portfolio already exists
            num_stocks = self.stocks.count()
            if num_stocks < 5:
                raise ValidationError('A portfolio must contain at least 5 stocks.')
            if num_stocks > 50:
                raise ValidationError('A portfolio can contain a maximum of 50 stocks.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.user.username})"


class PortfolioStock(models.Model):
    portfolio = models.ForeignKey('portfolio.Portfolio', on_delete=models.CASCADE, related_name='portfolio_stocks')
    stock = models.ForeignKey('equity_optimizer.Stock', on_delete=models.CASCADE, related_name='portfolio_stocks')
    quantity = models.FloatField()

    objects = PortfolioManager()

    class Meta:
        unique_together = ('portfolio', 'stock')

    def __str__(self):
        return f"{self.stock.ticker} - {self.quantity} shares in {self.portfolio.name}"


class PortfolioValueHistory(CreatedAtMixin, UpdatedAtMixin):
    portfolio = models.ForeignKey('portfolio.Portfolio', on_delete=models.CASCADE, related_name='value_history')
    date = models.DateField(default=timezone.now)
    value = models.FloatField()
    daily_return = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ('portfolio', 'date')
        indexes = [
            models.Index(fields=['portfolio', 'date']),
        ]

    def __str__(self):
        return f"{self.portfolio.name} value on {self.date}: ${self.value:.2f}"
