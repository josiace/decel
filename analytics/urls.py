from django.urls import path
from . import views
from . import admin_views

app_name = 'analytics'

urlpatterns = [
    path('', views.user_analytics, name='user_analytics'),
    path('activity-log/', views.activity_log, name='activity_log'),
    path('admin-dashboard/', admin_views.admin_analytics_dashboard, name='admin_analytics_dashboard'),
    path('admin-user-analytics/<int:user_id>/', admin_views.admin_user_analytics, name='admin_user_analytics'),
]
