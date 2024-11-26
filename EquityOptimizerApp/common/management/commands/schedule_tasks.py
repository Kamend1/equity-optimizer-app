from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, CrontabSchedule


class Command(BaseCommand):
    help = "Create periodic tasks for data updates"

    def handle(self, *args, **kwargs):

        schedule, created = CrontabSchedule.objects.get_or_create(
            minute='0',
            hour='1',  # CET is UTC+1
            day_of_week='*',
            day_of_month='*',
            month_of_year='*',
        )

        PeriodicTask.objects.update_or_create(
            crontab=schedule,
            name='Update All Data',
            task='tasks.update_all_data',
        )

        self.stdout.write(self.style.SUCCESS('Scheduled "Update All Data" task at 02:00 CET.'))
