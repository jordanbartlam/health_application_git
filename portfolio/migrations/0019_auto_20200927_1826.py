# Generated by Django 3.0.8 on 2020-09-27 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0018_auto_20200927_1823'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='date',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='withdrawal',
            name='date',
            field=models.DateField(auto_now_add=True),
        ),
    ]