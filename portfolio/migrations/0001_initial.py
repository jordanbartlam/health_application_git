# Generated by Django 3.0.8 on 2020-08-18 11:13

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Portfolio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text="Enter the name of the Portfolio eg. Jordan's Portfolio", max_length=200)),
                ('start_date', models.DateField(default=datetime.date(2019, 9, 18))),
                ('currency', models.CharField(default='GBP', help_text='Enter desired currency (e.g. GBP or USD).', max_length=200)),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': (('can_view_portfolios', 'View all portfolios'),),
            },
        ),
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticker', models.CharField(max_length=200)),
                ('date_bought', models.DateField()),
                ('number_bought', models.PositiveIntegerField(default=0, help_text='Number of shares held.')),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('portfolio', models.ManyToManyField(to='portfolio.Portfolio')),
            ],
        ),
        migrations.CreateModel(
            name='Crypto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticker', models.CharField(max_length=200)),
                ('date_bought', models.DateField()),
                ('number_bought', models.PositiveIntegerField(default=0, help_text='Number of crypto-currency instances held')),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('portfolio', models.ManyToManyField(to='portfolio.Portfolio')),
            ],
        ),
    ]