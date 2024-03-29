# Generated by Django 3.0.8 on 2020-08-19 12:39

import datetime
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0004_auto_20200818_2059'),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('activity', models.CharField(choices=[('WALK', 'Walk'), ('RUN', 'Run'), ('CYCLE', 'Cycle'), ('GYM', 'Gym'), ('OTHER', 'Other')], max_length=30)),
                ('time', models.DurationField(default=datetime.timedelta(0), help_text='Use format: H:MM:SS')),
                ('distance', models.FloatField(default=0, help_text='Kilometers. Leave as 0km if unsure.')),
                ('travel_avoided', models.CharField(choices=[('BUS', 'Bus'), ('TRAIN', 'Train'), ('CAR', 'Car'), ('PLANE', 'Plane'), ('OTHER', 'Other'), ('NONE', 'None')], max_length=30)),
                ('amount_saved', models.DecimalField(decimal_places=2, default=0, help_text='(£)', max_digits=6)),
            ],
        ),
        migrations.CreateModel(
            name='Withdrawal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('amount_withdrawn', models.DecimalField(decimal_places=2, default=0, help_text='(£)', max_digits=6)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('amount_paid', models.DecimalField(decimal_places=2, default=0, help_text='(£)', max_digits=6)),
                ('activity', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='portfolio.Activity')),
            ],
        ),
    ]
