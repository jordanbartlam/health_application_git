from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('help/', views.help, name='help'),
    path('profile/update/', views.ProfileUpdate.as_view(), name='profile_update'),
    path('myactivities/', views.ActivityByUserListView.as_view(), name='my-activities'),
    path('activity/create/', views.ActivityCreate.as_view(), name='activity_create'),
    path('activity/<int:pk>/update/', views.ActivityUpdate.as_view(), name='activity_update'),
    path('activity/<int:pk>/delete/', views.ActivityDelete.as_view(), name='activity_delete'),

    path('mypayments/', views.PaymentByUserListView.as_view(), name='my-payments'),
    path('payment/create/', views.PaymentCreate.as_view(), name='payment_create'),
    path('payment/<int:pk>/update/', views.PaymentUpdate.as_view(), name='payment_update'),
    path('payment/<int:pk>/delete/', views.PaymentDelete.as_view(), name='payment_delete'),

    path('mywithdrawals/', views.WithdrawalByUserListView.as_view(), name='my-withdrawals'),
    path('withdrawal/create/', views.WithdrawalCreate.as_view(), name='withdrawal_create'),
    path('withdrawal/<int:pk>/update/', views.WithdrawalUpdate.as_view(), name='withdrawal_update'),
    path('withdrawal/<int:pk>/delete/', views.WithdrawalDelete.as_view(), name='withdrawal_delete'),

    path('health/', views.health, name='health'),
    path('environmental/', views.environmental, name='environmental'),
    path('wealth/', views.wealth, name='wealth'),
    path('wealth/healthfund/analysis/', views.healthfund_analysis, name='healthfund_analysis'),
    path('wealth/esgfund/analysis/', views.esgfund_analysis, name='esgfund_analysis'),

    path('signup/', views.signup, name='signup'),
]