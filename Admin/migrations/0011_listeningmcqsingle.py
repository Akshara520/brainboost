# Generated by Django 5.1.5 on 2025-02-05 03:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Admin', '0010_readmcqmultiple'),
    ]

    operations = [
        migrations.CreateModel(
            name='ListeningMCQSingle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('audio', models.FileField(upload_to='audios/')),
                ('choice1', models.CharField(max_length=255)),
                ('choice2', models.CharField(max_length=255)),
                ('choice3', models.CharField(max_length=255)),
                ('choice4', models.CharField(max_length=255)),
                ('answer', models.CharField(max_length=255)),
            ],
        ),
    ]
