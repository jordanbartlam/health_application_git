from django.contrib import admin
from .models import Profile, Activity

# Register your models here.
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'date_of_birth', 'sex', 'nationality', 'weight', 'job', 'email')

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('date', 'activity', 'time', 'distance', 'travel_avoided', 'amount_saved')

