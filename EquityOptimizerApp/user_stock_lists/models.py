from django.contrib.auth.models import User
from django.db import models

from EquityOptimizerApp.equity_optimizer.models import Stock
from EquityOptimizerApp.mixins import CreatedAtMixin, UpdatedAtMixin


# Create your models here.
class FavoriteStockList(CreatedAtMixin, UpdatedAtMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    stocks = models.ManyToManyField(Stock, blank=True)
