# Generated by Django 5.0.7 on 2024-08-22 09:23

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equity_optimizer', '0003_stockdata_created_at_stockdata_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False),
        ),
        migrations.AddField(
            model_name='stock',
            name='updated_at',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False),
        ),
    ]
