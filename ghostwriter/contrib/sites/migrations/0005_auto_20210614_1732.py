# Generated by Django 3.0.10 on 2021-06-14 17:32

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("sites", "0004_auto_20210406_0058"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="site",
            options={"ordering": ("domain",), "verbose_name": "site", "verbose_name_plural": "sites"},
        ),
    ]
