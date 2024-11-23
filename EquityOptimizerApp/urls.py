from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('stocks/', include('EquityOptimizerApp.equity_optimizer.urls')),
    path('', include('EquityOptimizerApp.common.urls')),
    path('accounts/', include('EquityOptimizerApp.accounts.urls')),
    path('portfolio/', include('EquityOptimizerApp.portfolio.urls')),
    path('user_stock_lists/', include('EquityOptimizerApp.user_stock_lists.urls')),
    path('currencies/', include('EquityOptimizerApp.currencies.urls')),
]

urlpatterns += [
    # Generate the OpenAPI schema
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    # Swagger UI
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Redoc
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
