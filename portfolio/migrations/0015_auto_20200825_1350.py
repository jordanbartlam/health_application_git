# Generated by Django 3.0.8 on 2020-08-25 12:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0014_auto_20200825_1313'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='portfolio',
            name='owner',
        ),
        migrations.RemoveField(
            model_name='stock',
            name='owner',
        ),
        migrations.RemoveField(
            model_name='stock',
            name='portfolio',
        ),
        migrations.DeleteModel(
            name='Crypto',
        ),
        migrations.DeleteModel(
            name='Portfolio',
        ),
        migrations.DeleteModel(
            name='Stock',
        ),
    ]
