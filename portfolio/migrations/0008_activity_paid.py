# Generated by Django 3.0.8 on 2020-08-19 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0007_auto_20200819_1500'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='paid',
            field=models.CharField(choices=[('Y', 'Yes'), ('N', 'No')], default='N', max_length=1),
        ),
    ]
