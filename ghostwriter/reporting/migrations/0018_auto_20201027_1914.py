# Generated by Django 3.0.10 on 2020-10-27 19:14

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("reporting", "0017_auto_20201019_2318"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="reporttemplate",
            options={
                "ordering": ["doc_type", "client", "name"],
                "verbose_name": "Report template",
                "verbose_name_plural": "Report templates",
            },
        ),
        migrations.RemoveField(
            model_name="reporttemplate",
            name="default",
        ),
    ]
