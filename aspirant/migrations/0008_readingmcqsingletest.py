# Generated by Django 5.1.6 on 2025-02-14 11:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Admin', '0021_listeningcorrectsummary_listeningfillblanks_and_more'),
        ('aspirant', '0007_delete_readingmcqsingletest'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReadingMCQSingleTest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student', models.CharField(max_length=255)),
                ('reg_id', models.IntegerField()),
                ('answer', models.CharField(blank=True, max_length=255, null=True)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Admin.readmcqsingle')),
            ],
        ),
    ]
