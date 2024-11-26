from django.contrib import admin
from django_celery_beat.models import PeriodicTask

# Optionally customize the PeriodicTask admin interface
@admin.register(PeriodicTask)
class PeriodicTaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'enabled', 'last_run_at', 'total_run_count',)
    search_fields = ('name',)
    list_filter = ('enabled',)
