# Generated by Django 3.2.11 on 2022-02-09 19:05

# Django Imports
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shepherd', '0037_convert_dns_record_to_json'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='domain',
            name='dns_record',
        ),
    ]
