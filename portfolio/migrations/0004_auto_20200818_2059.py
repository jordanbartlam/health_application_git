# Generated by Django 3.0.8 on 2020-08-18 19:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0003_auto_20200818_2057'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='weight',
            field=models.IntegerField(blank=True, help_text='Input weight in terms of kilograms.', null=True),
        ),
    ]