from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('home/', views.home_authenticated, name='home_authenticated'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('wallet/', views.wallet, name='wallet'),
    path('wallet/streak-shield/', views.streak_shield, name='streak_shield'),
    path('referral/', views.referral_page, name='referral'),
    path('promo-codes/', views.promo_codes_page, name='promo_codes'),
    path('apply-promo-code/', views.apply_promo_code, name='apply_promo_code'),
    path('admin/user/<int:user_id>/', views.admin_user_detail, name='admin_user_detail'),
    path('api/xp-evolution/', views.xp_evolution_api, name='xp_evolution_api'),
    path('api/level-progress/', views.level_progress_api, name='level_progress_api'),
    path('country/create/', views.country_create, name='country_create'),
    path('grade-level/create/', views.grade_level_create, name='grade_level_create'),
    path('admin/visitor-statistics/', views.visitor_statistics, name='visitor_statistics'),
]
