from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('plans/', views.subscription_plans, name='plans'),
    path('subscribe/<int:plan_id>/', views.subscribe, name='subscribe'),
    path('my-subscription/', views.my_subscription, name='my_subscription'),
    path('subscription/<int:subscription_id>/', views.subscription_detail, name='detail'),
    path('subscription/<int:subscription_id>/cancel/', views.cancel_subscription, name='cancel'),
    path('upgrade/', views.upgrade_subscription, name='upgrade'),
]
