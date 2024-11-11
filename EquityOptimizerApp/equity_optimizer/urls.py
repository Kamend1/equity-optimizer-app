from django.urls import path
from . import views

urlpatterns = [
    path('simulation/', views.simulation, name='simulation'),
    path('add/', views.add_stock, name='add_stock'),
    path('analyze/<str:ticker>/', views.analyze_stock, name='analyze_stock'),
    path('stocks/', views.StockListView.as_view(), name='stock_list'),
    path('stocks/<str:ticker>/', views.StockDetailView.as_view(), name='stock_detail'),
    path('update_stocks/', views.update_stocks_view, name='update_stocks'),
    path('get-progress/', views.get_progress, name='get_progress'),
    path('<str:ticker>/historical_data/', views.StockDataListView.as_view(), name='stock_data_list'),
]