# Generated by Django 5.0.7 on 2024-11-11 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0002_alter_portfolio_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='portfolio',
            name='public',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
