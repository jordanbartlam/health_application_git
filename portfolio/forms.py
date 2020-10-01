from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _



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


# class MLTForm(forms.Form):
#     amount_purchased = forms.IntegerField(required=False, label='Buy MLT', initial=0)
#     amount_sold = forms.IntegerField(required=False, label='Sell MLT', initial=0)
#     amount_retired = forms.IntegerField(required=False, label='Retire MLT', initial=0)
#
#     def clean_amount_purchased(self):
#         data = self.cleaned_data['amount_purchased']
#
#         if data < 0:
#             raise ValidationError(_('Must be either 0 or a positive number.'))
#
#         return data
#
#     def clean_amount_sold(self):
#         data = self.cleaned_data['amount_sold']
#
#         if data < 0:
#             raise ValidationError(_('Must be either 0 or a positive number.'))
#
#         return data
#
#     def clean_amount_retired(self):
#         data = self.cleaned_data['amount_retired']
#
#         if data < 0:
#             raise ValidationError(_('Must be either 0 or a positive number.'))
#
#         return data