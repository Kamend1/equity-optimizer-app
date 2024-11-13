from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('stocks/', include('EquityOptimizerApp.equity_optimizer.urls')),
    path('', include('EquityOptimizerApp.common.urls')),
    path('accounts/', include('EquityOptimizerApp.accounts.urls')),
    path('portfolio/', include('EquityOptimizerApp.portfolio.urls')),
    path('user_stock_lists/', include('EquityOptimizerApp.user_stock_lists.urls')),
    path('currencies/', include('EquityOptimizerApp.currencies.urls')),
]
