from django.contrib import admin
from .models import Stock, StockData


# Register your models here.
@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'name', 'sector', 'market_cap')
    search_fields = ('ticker', 'name', 'sector', 'market_cap')


@admin.register(StockData)
class StockDataAdmin(admin.ModelAdmin):
    list_display = ['stock', 'date', 'open', 'high', 'low','close', 'adj_close', 'daily_return', 'trend']
