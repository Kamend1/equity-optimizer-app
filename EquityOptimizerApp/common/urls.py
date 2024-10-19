from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),  # Landing page URL
    path('home/', views.home, name='home'),  # Home page URL after login/register
    path('about/', views.about, name='about'),  # About page
    path('contact/', views.contact, name='contact'),  # Contacts page
    path('contact/success/', views.contact_success, name='contact_success'),
]