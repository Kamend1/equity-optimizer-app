from django.urls import path
from . import views

urlpatterns = [
    path('', views.CurrencyListView.as_view(), name='currency-list'),
    path('<int:pk>/', views.CurrencyDetailView.as_view(), name='currency-detail'),
    path('create/', views.CurrencyCreateView.as_view(), name='currency-create'),
    path('<int:pk>/edit/', views.CurrencyEditView.as_view(), name='currency-edit'),
    path('exchange-rates/<str:base_code>/<str:target_code>/', views.ExchangeRateListView.as_view(), name='exchange-rate-list'),
]
