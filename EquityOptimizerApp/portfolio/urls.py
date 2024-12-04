from django.urls import path, include
from . import views

urlpatterns = [
    path('personal-portfolios/', views.PersonalPortfolioListView.as_view(), name='personal-portfolios'),
    path('public-portfolios/', views.PublicPortfolioListView.as_view(), name='public-portfolios'),

    path('<int:portfolio_id>/', include([
        path('detail/', views.PortfolioDetailView.as_view(), name='portfolio-detail'),
        path('edit/', views.PortfolioEditView.as_view(), name='portfolio-edit'),
        path('value-history/', views.PortfolioValueHistoryListView.as_view(), name='portfolio-value-history'),
        path('toggle-upvote/', views.toggle_upvote, name='portfolio-toggle-upvote'),
        ])
    ),
    path('save-portfolio/', views.save_portfolio_view, name='save_portfolio'),
    path('update_portfolios/', views.update_portfolios_view, name='update_portfolios'),
    path('portfolios-performance/', views.portfolio_performance_view, name='portfolios-performance'),
]
