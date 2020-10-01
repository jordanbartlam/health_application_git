from django.db import models
from django.urls import reverse
from datetime import date, timedelta
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField(null=True, blank=True, help_text="Format: YYYY-MM-DD")

    SEX_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('U', 'Unsure'),
    )

    sex = models.CharField(max_length=1, choices=SEX_CHOICES)
    email = models.EmailField(max_length=254, help_text='Required. Enter a valid email address.')
    nationality = CountryField()
    weight = models.IntegerField(null=True, blank=True, help_text='Input weight in terms of kilograms.')

    JOB_CHOICES = (
        ('AGRICULTURE', 'Agriculture, Food and Natural Resources'),
        ('CONSTRUCTION', 'Architecture and Construction'),
        ('ARTS', 'Arts, Audio/Video Technology and Communication'),
        ('BUSINESS', 'Business Management and Administration'),
        ('EDUCATION', 'Education and Training'),
        ('FINANCE', 'Finance'),
        ('GOV', 'Government and Public Administration'),
        ('HEALTH', 'Health Sciences'),
        ('TOURISM', 'Hospitality and Tourism'),
        ('HUMAN_SERVICES', 'Human Services'),
        ('IT', 'Information Technology'),
        ('LAW', 'Law, Public Safety, Corrections and Security'),
        ('MANUFACTURING', 'Manufacturing'),
        ('MARKETING', 'Marketing, Sales and Service'),
    )

    job = models.CharField(max_length=60, choices=JOB_CHOICES)
    weekly_hours_of_exercise = models.DurationField(default=timedelta(), help_text='Use format: HH:MM:SS')

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def update_profile_signal(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

class Activity(models.Model):

    date = models.DateField(default=date.today)

    ACTIVITIES = (
        ('WALK', 'Walk'),
        ('RUN', 'Run'),
        ('CYCLE', 'Cycle'),
        ('GYM', 'Gym'),
        ('OTHER', 'Other'),
    )

    activity = models.CharField(max_length=30, choices=ACTIVITIES)
    time = models.DurationField(default=timedelta(), help_text='Use format: HH:MM:SS')
    distance = models.FloatField(default=0, help_text='Kilometers (1km = 0.6miles). Leave as 0km if unsure.')

    TRAVEL = (
        ('BUS', 'Bus'),
        ('TRAIN', 'Train'),
        ('CAR', 'Car'),
        ('PLANE', 'Plane'),
        ('OTHER', 'Other'),
        ('NONE', 'None'),
    )

    travel_avoided = models.CharField(max_length=30, choices=TRAVEL)
    amount_saved = models.DecimalField(default=0.00, max_digits=6, decimal_places=2, help_text='(£)')
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    PAID = (
        ('Y', 'Yes'),
        ('N', 'No'),
    )

    paid = models.CharField(max_length=1, choices=PAID, default='N')

    class Meta:
        verbose_name_plural = "activities"
        ordering = ['-date']

    def convert_time(self):
        """Convert time into a nicer format"""
        total_seconds = int(self.time.total_seconds())
        hours = total_seconds // 3600
        minutes = round((total_seconds % 3600) / 60)
        if minutes == 60:
            hours += 1
            minutes = 0
        if hours and minutes:
            return '{}h {}m'.format(hours, minutes)
        elif hours:
            return '{}h'.format(hours)
        else:
            return '{}m'.format(minutes)

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.convert_time()} {self.get_activity_display()} on {self.date}'

class MLT_bought(models.Model):
    amount = models.PositiveIntegerField(default=0)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

class MLT_sold(models.Model):
    amount = models.PositiveIntegerField(default=0)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

class MLT_retired(models.Model):
    amount = models.PositiveIntegerField(default=0)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)


class Payment(models.Model):
    date = models.DateField(default=date.today)
    amount_paid = models.DecimalField(default=0.00, max_digits=6, decimal_places=2, help_text='(£)')
    activity = models.ForeignKey(Activity, on_delete=models.SET_NULL, null=True, blank=True)

    PORTFOLIOS = (
        ('CASH', 'Cash'),
        ('HEALTH_TECH', 'Health Tech Fund'),
        ('ESG', 'Sustainability Fund'),
    )

    portfolio = models.CharField(max_length=100, choices=PORTFOLIOS, default='CASH')
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        """String for representing the Model object."""
        return f'£{self.amount_paid} paid on {self.date}'

    def save(self, *args, **kwargs):
        if (not self.pk) and (self.activity != None):
            Activity.objects.filter(pk=self.activity.id).update(paid='Y')
        super().save(*args, **kwargs)

class Withdrawal(models.Model):
    date = models.DateField(default=date.today)
    amount_withdrawn = models.DecimalField(default=0.00, max_digits=6, decimal_places=2, help_text='(£)')

    PORTFOLIOS = (
        ('CASH', 'Cash'),
        ('HEALTH_TECH', 'Health Tech Fund'),
        ('ESG', 'Sustainability Fund'),
    )

    portfolio = models.CharField(max_length=100, choices=PORTFOLIOS, default='CASH')
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        """String for representing the Model object."""
        return f'£{self.amount_withdrawn} withdrawn on {self.date}'
