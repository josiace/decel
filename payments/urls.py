from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('packs/', views.packs, name='packs'),
    path('checkout/<int:pack_id>/', views.create_checkout_session, name='create_checkout_session'),
    path('success/', views.checkout_success, name='checkout_success'),
    path('cancel/', views.checkout_cancel, name='checkout_cancel'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
    # Abonnements créateur
    path('subscription/checkout/<str:plan>/', views.create_subscription_session, name='create_subscription_session'),
    path('subscription/success/', views.subscription_success, name='subscription_success'),
    # Paiements alternatifs
    path('manual/<int:pack_id>/', views.manual_payment, name='manual_payment'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('recharge-code/', views.recharge_code, name='recharge_code'),
    path('my-orders/', views.my_orders, name='my_orders'),
]
