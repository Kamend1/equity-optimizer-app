from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule, SolarSchedule, ClockedSchedule
from django_celery_results.models import TaskResult

# Register Celery Beat models
admin.site.register(IntervalSchedule)
admin.site.register(CrontabSchedule)
admin.site.register(SolarSchedule)
admin.site.register(ClockedSchedule)


@admin.register(TaskResult)
class TaskResultAdmin(admin.ModelAdmin):
    list_display = ('task_name', 'status', 'date_done', 'worker', 'result',)
    search_fields = ('task_name', 'worker',)
    list_filter = ('status', 'date_done',)

@admin.register(PeriodicTask)
class PeriodicTaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'enabled', 'last_run_at', 'total_run_count',)
    search_fields = ('name',)
    list_filter = ('enabled',)
