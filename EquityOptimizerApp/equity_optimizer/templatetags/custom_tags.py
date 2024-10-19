from django import template
from django.forms import BoundField
from django.urls import reverse

register = template.Library()


@register.simple_tag(takes_context=True)
def show_nav(context):
    path = context['request'].path
    login_url = reverse('login')
    logout_url = reverse('logout')
    landing_url = reverse('landing')
    register_url = reverse('register')

    # Check if the current path contains any of these URLs
    return not any(url in path for url in [landing_url, login_url, logout_url, register_url])


@register.filter(name='add_class')
def add_class(value, css_class):
    if isinstance(value, BoundField):
        return value.as_widget(attrs={'class': css_class})
    return value  # Return the value unchanged if it's not a BoundField