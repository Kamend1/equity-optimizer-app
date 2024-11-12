from django.urls import path
from . import views

urlpatterns = [
    path('portfolio/', views.portfolio, name='portfolio'),  # Portfolio page
    path('portfolio/<int:portfolio_id>/', views.PortfolioDetailView.as_view(), name='portfolio_detail'),
    path('save-portfolio/', views.save_portfolio_view, name='save_portfolio'),
    path('update_portfolios/', views.update_portfolios_view, name='update_portfolios'),
]
