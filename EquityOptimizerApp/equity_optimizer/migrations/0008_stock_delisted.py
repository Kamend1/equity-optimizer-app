# Generated by Django 5.0.7 on 2024-11-12 11:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equity_optimizer', '0007_remove_stock_average_daily_volume_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='delisted',
            field=models.BooleanField(default=False),
        ),
    ]