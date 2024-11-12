from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.portfolio, name='portfolio'),  # Portfolio page
    path('<int:portfolio_id>/', include([
        path('detail/', views.PortfolioDetailView.as_view(), name='portfolio-detail'),
        path('edit/', views.PortfolioEditView.as_view(), name='portfolio-edit'),
        path('value-history/', views.PortfolioValueHistoryListView.as_view(), name='portfolio-value-history'),
        ])
        ),
    path('save-portfolio/', views.save_portfolio_view, name='save_portfolio'),
    path('update_portfolios/', views.update_portfolios_view, name='update_portfolios'),
]
