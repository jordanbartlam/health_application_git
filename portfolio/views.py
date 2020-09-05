from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from .models import Profile, Activity, Payment, Withdrawal
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import Http404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import numpy as np


# Modules for data analysis:
import pandas as pd
import datetime
from .helper_functions import *

# Create your views here.
def index(request):
    """View function for home page of site."""
    return render(request, 'index.html', context={})

def about(request):
    """View function for about page of site."""
    return render(request, 'about.html', context={})

def help(request):
    """View function for help page of site."""
    return render(request, 'help.html', context={})

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.profile.first_name = form.cleaned_data.get('first_name')
            user.profile.last_name = form.cleaned_data.get('last_name')
            user.profile.date_of_birth = form.cleaned_data.get('date_of_birth')
            user.profile.sex = form.cleaned_data.get('sex')
            user.profile.email = form.cleaned_data.get('email')
            user.profile.weight = form.cleaned_data.get('weight')
            user.profile.nationality = form.cleaned_data.get('nationality')
            user.profile.job = form.cleaned_data.get('job')
            user.profile.weekly_hours_of_exercise = form.cleaned_data.get('weekly_hours_of_exercise')
            user.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

def health(request):
    """View function for health portfolio page of site."""
    activities = Activity.objects.filter(owner=request.user).order_by('date')
    first_activity = activities.first()
    last_activity = activities.last()

    # Calculate expected longevity
    if request.user.profile.nationality in ['GB', 'US', 'JP', 'FR', 'IT', 'DE', 'CA']:
        if request.user.profile.sex == 'F':
            longevity_expected = 83
        else:
            longevity_expected = 80
    else:
        if request.user.profile.sex == 'F':
            longevity_expected = 80
        else:
            longevity_expected = 78

    # Find the total activity time
    total_time = datetime.timedelta()
    for activity in activities:
        total_time += activity.time

    # Find average weekly exercise
    if activities:
        start_date = first_activity.date
        end_date = last_activity.date
    else:
        start_date = datetime.date.today()
        end_date = datetime.date.today()
    weeks_between = ((end_date-start_date).days) // 7

    if weeks_between == 0:
        weekly_activity = request.user.profile.weekly_hours_of_exercise
        weeks_between = 1
    elif weeks_between >= 14:
        weekly_activity = total_time // weeks_between
    else:
        weekly_activity = (request.user.profile.weekly_hours_of_exercise + (total_time // weeks_between)) // 2

    # The number of hours of exercise attributed to each form of exercise
    activity_dict = {}
    for activity in activities:
        activity_dict[activity.activity] = activity_dict.get(activity.activity, datetime.timedelta()) + activity.time

    # Convert this into average weekly hours for each type of exercise
    activity_dict.update((activity, time//weeks_between) for activity, time in activity_dict.items())

    longevity_earned = longevity_expected + calc_longevity(weekly_activity)
    mobility = calc_mobility(activity_dict)
    wellbeing = calc_wellness(longevity_expected, longevity_earned, mobility)

    longevity_radius = (longevity_earned - longevity_expected) * 10

    context = {
        'longevity_expected': longevity_expected,
        'longevity_earned': longevity_earned,
        'mobility': mobility,
        'wellbeing': wellbeing,
        'longevity_radius': longevity_radius,
    }

    return render(request, 'portfolio/health.html', context=context)

def environmental(request):
    """View function for health portfolio page of site."""
    activities = Activity.objects.filter(owner=request.user)
    all_activities = Activity.objects.all()

    # Find the total distance avoided by each mode of transport.
    activity_dict = {}
    for activity in activities:
        if activity.travel_avoided == 'NONE':
            continue
        activity_dict[activity.travel_avoided] = activity_dict.get(activity.travel_avoided, 0) + activity.distance

    # Convert distance for each mode of travel into CO2 emissions saved.
    emissions_dict = emissions_saved(activity_dict)

    # Combine the two:

    # Get the total distance and total personal emissions saved.
    # Find the total activity distance
    total_distance = 0
    for activity in activities:
        total_distance += activity.distance
    # Find total CO2 emissions saved
    total_emissions_saved = 0
    for value in emissions_dict.values():
        total_emissions_saved += value
    total_emissions_saved = round(total_emissions_saved, 2)

    # Find the overall carbon equivalent saved by ALL users.
    all_activity_dict = {}
    for all_activity in all_activities:
        all_activity_dict[all_activity.travel_avoided] = all_activity_dict.get(all_activity.travel_avoided, 0) + all_activity.distance
    all_emissions_dict = emissions_saved(all_activity_dict)
    all_total_emissions_saved = 0
    for value in all_emissions_dict.values():
        all_total_emissions_saved += value
    all_total_emissions_saved = round(all_total_emissions_saved, 2)

    # Calculate MLT Tokens:
    MLT_tokens = int(total_emissions_saved // 10)

    context = {
        'emissions_dict': emissions_dict,
        'activity_dict': activity_dict,
        'total_distance': total_distance,
        'total_emissions_saved': total_emissions_saved,
        'all_total_emissions_saved': all_total_emissions_saved,
        'MLT_tokens': MLT_tokens,
    }

    return render(request, 'portfolio/environmental.html', context=context)


def wealth(request):
    # Shared Variables
    currency = 'GBP'
    price_point = 'Adj Close'
    cash_payments = Payment.objects.filter(owner=request.user, portfolio='CASH').order_by('date')
    cash_withdrawals = Withdrawal.objects.filter(owner=request.user, portfolio='CASH').order_by('date')
    ESG_payments = Payment.objects.filter(owner=request.user, portfolio='ESG').order_by('date')
    ESG_withdrawals = Withdrawal.objects.filter(owner=request.user, portfolio='ESG').order_by('date')
    health_payments = Payment.objects.filter(owner=request.user, portfolio='HEALTH_TECH').order_by('date')
    health_withdrawals = Withdrawal.objects.filter(owner=request.user, portfolio='HEALTH_TECH').order_by('date')

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Cash:
    if cash_payments:
        cash_total_paid = 0
        cash_payment_amount_list = []
        cash_payment_date_list = []
        for payment in cash_payments:
            cash_total_paid += float(payment.amount_paid)
            cash_payment_date_list.append(payment.date)
            cash_payment_amount_list.append(float(payment.amount_paid))
        cash_total_withdrawn = 0
        cash_withdrawal_amount_list = []
        cash_withdrawal_date_list = []
        for withdrawal in cash_withdrawals:
            cash_total_withdrawn += float(withdrawal.amount_withdrawn)
            cash_withdrawal_date_list.append(withdrawal.date)
            cash_withdrawal_amount_list.append(float(withdrawal.amount_withdrawn))
        cash_net_paid = round(cash_total_paid - cash_total_withdrawn, 2)
        cash_payment_df = pd.DataFrame({'Date': cash_payment_date_list, 'Paid In': cash_payment_amount_list})
        cash_withdrawal_df = pd.DataFrame({'Date': cash_withdrawal_date_list, 'Paid Out': cash_withdrawal_amount_list})
        cash_df = pd.concat([cash_payment_df, cash_withdrawal_df]).fillna(0)
        cash_df.set_index('Date', inplace=True)
    else:
        cash_net_paid = 0
        cash_df = pd.DataFrame({'Paid In': [0], 'Paid Out': [0]})
    cash_df['Cash Net Payment'] = cash_df['Paid In'] - cash_df['Paid Out']

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # ESG
    if ESG_payments:
        ESG_start_date = ESG_payments.first().date
        if ESG_start_date == datetime.date.today():
            ESG_start_date = ESG_start_date - datetime.timedelta(days=3)
        ESG_investments = ['EME', 'CDNS', 'NEE', 'MSFT', 'HAS', 'HD', 'CRM']
        ESG_data = Prices(currency, ESG_start_date, ESG_investments, price_point)
        request.session['ESG_data'] = ESG_data
        ESG_prices = ESG_data.get_prices()
        request.session['ESG_prices'] = ESG_prices

        # Find total payments in versus total withdrawals
        ESG_total_paid = 0
        ESG_payment_amount_list = []
        ESG_payment_date_list = []
        for payment in ESG_payments:
            ESG_total_paid += float(payment.amount_paid)
            ESG_payment_date_list.append(payment.date)
            ESG_payment_amount_list.append(float(payment.amount_paid))
        ESG_total_withdrawn = 0
        ESG_withdrawal_amount_list = []
        ESG_withdrawal_date_list = []
        for withdrawal in ESG_withdrawals:
            ESG_total_withdrawn += float(withdrawal.amount_withdrawn)
            ESG_withdrawal_date_list.append(withdrawal.date)
            ESG_withdrawal_amount_list.append(float(withdrawal.amount_withdrawn))
        ESG_net_paid = ESG_total_paid - ESG_total_withdrawn
        request.session['ESG_net_paid'] = ESG_net_paid
        ESG_payment_df = pd.DataFrame({'Date': ESG_payment_date_list, 'Paid In': ESG_payment_amount_list})
        ESG_withdrawal_df = pd.DataFrame({'Date': ESG_withdrawal_date_list, 'Paid Out': ESG_withdrawal_amount_list})
        ESG_df = pd.concat([ESG_payment_df, ESG_withdrawal_df]).fillna(0)
        ESG_df.set_index('Date', inplace=True)
        ESG_df['ESG Net Payment'] = ESG_df['Paid In'] - ESG_df['Paid Out']

        # Number of units of the fund that we buy
        ESG_units_owned = 0
        for payment in ESG_payments:
            try:
                ESG_units_owned += (float(payment.amount_paid) / ESG_prices.loc[payment.date, 'Portfolio'])
            except KeyError:
                try:
                    ESG_units_owned += (float(payment.amount_paid) / ESG_prices.loc[
                        (payment.date - datetime.timedelta(days=4)), 'Portfolio'])
                except KeyError:
                    ESG_units_owned += (float(payment.amount_paid) / ESG_prices['Portfolio'].iloc[0])

        # Number of units of the fund that we sell
        ESG_units_sold = 0
        for payment in ESG_withdrawals:
            try:
                ESG_units_sold += (float(payment.amount_withdrawn) / ESG_prices.loc[payment.date, 'Portfolio'])
            except KeyError:
                try:
                    ESG_units_sold += (float(payment.amount_withdrawn) / ESG_prices.loc[
                        (payment.date - datetime.timedelta(days=4)), 'Portfolio'])
                except KeyError:
                    ESG_units_sold += (float(payment.amount_withdrawn) / ESG_prices['Portfolio'].iloc[0])

        # Net units that we hold
        ESG_net_units = ESG_units_owned - ESG_units_sold

        # Find the current value (units x current price)
        ESG_value = round(ESG_prices['Portfolio'].iloc[-1] * ESG_net_units, 2)
        request.session['ESG_value'] = ESG_value
    else:
        ESG_value = 0
        ESG_net_paid = 0
        ESG_df = pd.DataFrame({'Paid In': [0], 'Paid Out': [0]})
        ESG_df['ESG Net Payment'] = ESG_df['Paid In'] - ESG_df['Paid Out']

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # Health
    if health_payments:
        health_start_date = health_payments.first().date
        if health_start_date == datetime.date.today():
            health_start_date = health_start_date - datetime.timedelta(days=3)
        health_investments = ['QDEL', 'LVGO', 'CTLT', 'EW', 'ABMD', 'TDOC', 'INCY', 'TRHC', 'ILMN']
        health_data = Prices(currency, health_start_date, health_investments, price_point)
        request.session['health_data'] = health_data

        health_prices = health_data.get_prices()
        request.session['health_prices'] = health_prices

        # Find total payments in versus total withdrawals
        health_total_paid = 0
        health_payment_amount_list = []
        health_payment_date_list = []
        for payment in health_payments:
            health_total_paid += float(payment.amount_paid)
            health_payment_date_list.append(payment.date)
            health_payment_amount_list.append(float(payment.amount_paid))
        health_total_withdrawn = 0
        health_withdrawal_amount_list = []
        health_withdrawal_date_list = []
        for withdrawal in health_withdrawals:
            health_total_withdrawn += float(withdrawal.amount_withdrawn)
            health_withdrawal_date_list.append(withdrawal.date)
            health_withdrawal_amount_list.append(float(withdrawal.amount_withdrawn))
        health_net_paid = health_total_paid - health_total_withdrawn
        request.session['health_net_paid'] = health_net_paid
        health_payment_df = pd.DataFrame({'Date': health_payment_date_list, 'Paid In': health_payment_amount_list})
        health_withdrawal_df = pd.DataFrame({'Date': health_withdrawal_date_list, 'Paid Out': health_withdrawal_amount_list})
        health_df = pd.concat([health_payment_df, health_withdrawal_df]).fillna(0)
        health_df.set_index('Date', inplace=True)
        health_df['Health Net Payment'] = health_df['Paid In'] - health_df['Paid Out']

        health_units_owned = 0
        for payment in health_payments:
            try:
                health_units_owned += (float(payment.amount_paid) / health_prices.loc[payment.date, 'Portfolio'])
            except KeyError:
                try:
                    health_units_owned += (float(payment.amount_paid) / health_prices.loc[
                        (payment.date - datetime.timedelta(days=4)), 'Portfolio'])
                except KeyError:
                    health_units_owned += (float(payment.amount_paid) / health_prices['Portfolio'].iloc[0])

        # Number of units of the fund that we sell
        health_units_sold = 0
        for payment in health_withdrawals:
            try:
                health_units_sold += (float(payment.amount_withdrawn) / health_prices.loc[payment.date, 'Portfolio'])
            except KeyError:
                try:
                    health_units_sold += (float(payment.amount_withdrawn) / health_prices.loc[
                        (payment.date - datetime.timedelta(days=4)), 'Portfolio'])
                except KeyError:
                    health_units_sold += (float(payment.amount_withdrawn) / health_prices['Portfolio'].iloc[0])

        # Net units that we hold
        health_net_units = health_units_owned - health_units_sold

        # Find the current value (units x current price)
        health_value = round(health_prices['Portfolio'].iloc[-1] * health_net_units, 2)
        request.session['health_value'] = health_value
    else:
        health_value = 0
        health_net_paid = 0
        health_df = pd.DataFrame({'Paid In': [0], 'Paid Out': [0]})
        health_df['Health Net Payment'] = health_df['Paid In'] - health_df['Paid Out']

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # Find totals
    total_value = round(float(cash_net_paid) + float(ESG_value) + float(health_value), 2)
    total_net_paid = round(float(cash_net_paid) + float(health_net_paid) + float(ESG_net_paid), 2)

    total_df = pd.concat([cash_df, ESG_df, health_df]).fillna(0)
    print(total_df)
    print(total_df['Cash Net Payment'])
    print(total_df['ESG Net Payment'])
    print(total_df['Health Net Payment'])
    total_df['Total Net Payment'] = total_df['Cash Net Payment'] + total_df['ESG Net Payment'] + total_df['Health Net Payment']
    total_df['Total Net Payment'] = total_df['Total Net Payment'].cumsum()
    total_dates = total_df.index.to_list()
    total_dates = [str(total_date) for total_date in total_dates]
    total_net_paid_list = total_df['Total Net Payment'].to_list()
    cash_net_paid_list = total_df['Cash Net Payment'].cumsum().to_list()
    ESG_net_paid_list = total_df['ESG Net Payment'].cumsum().to_list()
    health_net_paid_list = total_df['Health Net Payment'].cumsum().to_list()

    context = {
        'cash_net_paid': cash_net_paid,
        'health_value': health_value,
        'ESG_value': ESG_value,
        'health_net_paid': health_net_paid,
        'ESG_net_paid': ESG_net_paid,
        'total_net_paid': total_net_paid,
        'total_value': total_value,
        'cash_net_paid_list': cash_net_paid_list,
        'ESG_net_paid_list': ESG_net_paid_list,
        'health_net_paid_list': health_net_paid_list,
        'total_dates': total_dates,
        'total_net_paid_list': total_net_paid_list,
    }

    return render(request, 'portfolio/wealth.html', context=context)


def healthfund_analysis(request):
    payments = Payment.objects.filter(owner=request.user, portfolio='HEALTH_TECH').order_by('date')
    withdrawals = Withdrawal.objects.filter(owner=request.user, portfolio='HEALTH_TECH').order_by('date')

    if payments:
        health_net_paid = request.session['health_net_paid']

        currency = 'GBP'
        price_point = 'Adj Close'
        start_date = payments.first().date
        if start_date == datetime.date.today():
            start_date = start_date - datetime.timedelta(days=3)
        health_investments = ['QDEL', 'LVGO', 'CTLT', 'EW', 'ABMD', 'TDOC', 'INCY', 'TRHC', 'ILMN']
        health_data = request.session['health_data']

        names_prices_returns = health_data.get_names_prices_returns()

        # Line Chart
        health_prices = request.session['health_prices']
        portfolio_prices = health_prices['Portfolio'].values.tolist()
        axis_labels = health_prices.index.values.tolist()
        axis_labels = [str(axis_label) for axis_label in axis_labels]

        # PIE CHART
        health_value = request.session['health_value']
        pie_values = [health_value/len(health_investments) for i in range(len(health_investments))]
        pie_values = list(map(lambda x: round(x, 3), pie_values))
        pie_values = list(map(lambda x: float(x), pie_values))
        pie_labels = health_investments.copy()

        # BAR CHART
        sorted_headings, sorted_returns = health_data.order_by_total_return()

        # LINE CHART 2
        index_ticker = "^GSPC"
        benchmarked_returns = health_data.get_benchmarked_returns(index_ticker, currency, start_date, price_point)
        portfolio_returns = benchmarked_returns['Portfolio'].values.tolist()
        index_returns = benchmarked_returns[index_ticker].values.tolist()
        benchmarked_axis_labels = benchmarked_returns.index.values.tolist()
        benchmarked_axis_labels = [str(axis_label) for axis_label in benchmarked_axis_labels]

        context = {
            'names_prices_returns': names_prices_returns,
            'portfolio_prices': portfolio_prices,
            'axis_labels': axis_labels,
            'pie_values': pie_values,
            'pie_labels': pie_labels,
            'sorted_headings': sorted_headings,
            'sorted_returns': sorted_returns,
            'portfolio_returns': portfolio_returns,
            'index_returns': index_returns,
            'benchmarked_axis_labels': benchmarked_axis_labels,
            'index_ticker': index_ticker,
        }
    else:
        context = {}

    return render(request, 'portfolio/healthfund_analysis.html', context=context)


def esgfund_analysis(request):
    payments = Payment.objects.filter(owner=request.user, portfolio='ESG').order_by('date')
    withdrawals = Withdrawal.objects.filter(owner=request.user, portfolio='ESG').order_by('date')

    if payments:
        # Find total payments in versus total withdrawals
        ESG_net_paid = request.session['ESG_net_paid']

        currency = 'GBP'
        price_point = 'Adj Close'
        start_date = payments.first().date
        if start_date == datetime.date.today():
            start_date = start_date - datetime.timedelta(days=3)
        ESG_investments = ['EME', 'CDNS', 'NEE', 'MSFT', 'HAS', 'HD', 'CRM']

        ESG_data = request.session['ESG_data']
        names_prices_returns = ESG_data.get_names_prices_returns()

        # Line Chart
        ESG_prices = request.session['ESG_prices']
        portfolio_prices = ESG_prices['Portfolio'].values.tolist()
        axis_labels = ESG_prices.index.values.tolist()
        axis_labels = [str(axis_label) for axis_label in axis_labels]

        # PIE CHART
        ESG_value = request.session['ESG_value']
        pie_values = [ESG_value/len(ESG_investments) for i in range(len(ESG_investments))]
        pie_values = list(map(lambda x: round(x, 3), pie_values))
        pie_values = list(map(lambda x: float(x), pie_values))
        pie_labels = ESG_investments.copy()

        # BAR CHART
        sorted_headings, sorted_returns = ESG_data.order_by_total_return()

        # LINE CHART 2
        index_ticker = "^GSPC"
        benchmarked_returns = ESG_data.get_benchmarked_returns(index_ticker, currency, start_date, price_point)
        portfolio_returns = benchmarked_returns['Portfolio'].values.tolist()
        index_returns = benchmarked_returns[index_ticker].values.tolist()
        benchmarked_axis_labels = benchmarked_returns.index.values.tolist()
        benchmarked_axis_labels = [str(axis_label) for axis_label in benchmarked_axis_labels]

        context = {
            'names_prices_returns': names_prices_returns,
            'portfolio_prices': portfolio_prices,
            'axis_labels': axis_labels,
            'pie_values': pie_values,
            'pie_labels': pie_labels,
            'sorted_headings': sorted_headings,
            'sorted_returns': sorted_returns,
            'portfolio_returns': portfolio_returns,
            'index_returns': index_returns,
            'benchmarked_axis_labels': benchmarked_axis_labels,
            'index_ticker': index_ticker,
        }
    else:
        context = {}

    return render(request, 'portfolio/esgfund_analysis.html', context=context)

class ProfileUpdate(LoginRequiredMixin, UpdateView):
    model = Profile
    fields = ['first_name', 'last_name', 'date_of_birth', 'sex', 'email', 'weight', 'nationality', 'job', 'weekly_hours_of_exercise']
    success_url = reverse_lazy('index')

    def get_object(self, queryset=None):
        return self.request.user.profile

class ActivityByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing portfolios owned by current user."""
    model = Activity
    template_name = 'portfolio/activity_list_owned_user.html'
    paginate_by = 7

    def get_queryset(self):
        return Activity.objects.filter(owner=self.request.user)

class ActivityCreate(LoginRequiredMixin, CreateView):
    model = Activity
    fields = ['date', 'activity', 'time', 'distance', 'travel_avoided', 'amount_saved']
    success_url = reverse_lazy('my-activities')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class ActivityUpdate(LoginRequiredMixin, UpdateView):
    model = Activity
    fields = ['date', 'activity', 'time', 'distance', 'travel_avoided', 'amount_saved', 'paid']
    success_url = reverse_lazy('my-activities')

class ActivityDelete(LoginRequiredMixin, DeleteView):
    model = Activity
    success_url = reverse_lazy('my-activities')

class PaymentByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing portfolios owned by current user."""
    model = Payment
    template_name = 'portfolio/payment_list_owned_user.html'
    paginate_by = 7

    def get_queryset(self):
        return Payment.objects.filter(owner=self.request.user)

class PaymentCreate(LoginRequiredMixin, CreateView):
    model = Payment
    fields = ['date', 'amount_paid', 'activity', 'portfolio']
    success_url = reverse_lazy('my-payments')

    def get_form(self, form_class=None):
        form = super().get_form(form_class=None)
        form.fields['activity'].queryset = Activity.objects.filter(owner=self.request.user)
        return form

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class PaymentUpdate(LoginRequiredMixin, UpdateView):
    model = Payment
    fields = ['date', 'amount_paid', 'activity', 'portfolio']
    success_url = reverse_lazy('my-payments')

    def get_form(self, form_class=None):
        form = super().get_form(form_class=None)
        form.fields['activity'].queryset = Activity.objects.filter(owner=self.request.user)
        return form

class PaymentDelete(LoginRequiredMixin, DeleteView):
    model = Payment
    success_url = reverse_lazy('my-payments')

class WithdrawalByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing portfolios owned by current user."""
    model = Withdrawal
    template_name = 'portfolio/withdrawal_list_owned_user.html'
    paginate_by = 7

    def get_queryset(self):
        return Withdrawal.objects.filter(owner=self.request.user)

class WithdrawalCreate(LoginRequiredMixin, CreateView):
    model = Withdrawal
    fields = ['date', 'amount_withdrawn', 'portfolio']
    success_url = reverse_lazy('my-withdrawals')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class WithdrawalUpdate(LoginRequiredMixin, UpdateView):
    model = Withdrawal
    fields = ['date', 'amount_withdrawn', 'portfolio']
    success_url = reverse_lazy('my-withdrawals')

class WithdrawalDelete(LoginRequiredMixin, DeleteView):
    model = Withdrawal
    success_url = reverse_lazy('my-withdrawals')
