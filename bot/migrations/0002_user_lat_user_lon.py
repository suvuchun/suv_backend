# Generated by Django 5.2 on 2025-06-10 06:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='lat',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='lon',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
