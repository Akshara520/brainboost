# Generated by Django 5.1.7 on 2025-03-13 11:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aspirant', '0019_readingtestresult_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='readingtestresult',
            name='date',
        ),
    ]
