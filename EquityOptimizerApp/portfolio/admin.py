from django.contrib import admin

from EquityOptimizerApp.portfolio.models import Portfolio, PortfolioStock


# Register your models here.

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    pass


@admin.register(PortfolioStock)
class PortfolioStockAdmin(admin.ModelAdmin):
    pass
