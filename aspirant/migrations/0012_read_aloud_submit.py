# Generated by Django 5.1.6 on 2025-02-22 04:08

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Admin', '0021_listeningcorrectsummary_listeningfillblanks_and_more'),
        ('aspirant', '0011_final_result'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Read_aloud_submit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mark', models.IntegerField(default=0, null=True)),
                ('questions', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Admin.readaloud')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
