# Generated by Django 3.2.11 on 2022-05-10 19:49

# Django Imports
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("shepherd", "0039_auto_20220510_1909"),
    ]

    operations = [
        migrations.RunSQL(
            'ALTER TABLE shepherd_auxserveraddress ALTER COLUMN "primary" SET DEFAULT FALSE;',
        ),
        migrations.RunSQL(
            "ALTER TABLE shepherd_domain ALTER COLUMN auto_renew SET DEFAULT FALSE;",
        ),
        migrations.RunSQL(
            "ALTER TABLE shepherd_domain ALTER COLUMN expired SET DEFAULT FALSE;",
        ),
        migrations.RunSQL(
            "ALTER TABLE shepherd_domain ALTER COLUMN reset_dns SET DEFAULT FALSE;",
        ),
        migrations.RunSQL(
            "ALTER TABLE shepherd_domainserverconnection ALTER COLUMN subdomain SET DEFAULT '*';",
        ),
    ]
