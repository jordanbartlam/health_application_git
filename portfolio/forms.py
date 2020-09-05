from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from datetime import date, timedelta

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    date_of_birth = forms.DateField(help_text="Format: YYYY-MM-DD")

    SEX_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('U', 'Unsure'),
    )

    sex = forms.ChoiceField(choices=SEX_CHOICES)
    email = forms.EmailField(max_length=254, help_text='Required. Enter a valid email address.')
    nationality = CountryField().formfield()
    weight = forms.IntegerField(help_text='Input weight in terms of kilograms.')

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

    job = forms.ChoiceField(choices=JOB_CHOICES)
    weekly_hours_of_exercise = forms.DurationField(help_text='Use format: HH:MM:SS')

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'date_of_birth', 'sex', 'nationality', 'weight', 'job', 'weekly_hours_of_exercise', 'username', 'email', 'password1', 'password2',)


