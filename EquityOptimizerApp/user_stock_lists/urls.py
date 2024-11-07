from django.urls import path
from . import views

urlpatterns = [
    path('create_list/', views.UserStockListCreateView.as_view(), name='create_list'),
    path('user_lists/', views.UserListsMain.as_view(), name='stock_lists'),
    path('stock_search/', views.stock_search, name='stock_search'),
    path('<int:pk>/', views.UserListsDeleteView.as_view(), name='delete-list')
]