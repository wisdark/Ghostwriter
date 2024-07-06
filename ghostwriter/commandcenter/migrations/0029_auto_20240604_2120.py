# Generated by Django 3.2.19 on 2024-06-04 21:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commandcenter', '0028_auto_20240429_1912'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reportconfiguration',
            name='prefix_figure',
            field=models.CharField(default=' – ', help_text='Unicode character to place between the label and your figure caption in Word reports', max_length=255, verbose_name='Character Before Figure Captions'),
        ),
        migrations.AlterField(
            model_name='reportconfiguration',
            name='prefix_table',
            field=models.CharField(default=' – ', help_text='Unicode character to place between the label and your table caption in Word reports', max_length=255, verbose_name='Character Before Table Titles'),
        ),
    ]