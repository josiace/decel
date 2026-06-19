from django.contrib import admin
from .models import UserActivity, UserAnalytics


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_type', 'created_at', 'ip_address']
    list_filter = ['activity_type', 'created_at']
    search_fields = ['user__email', 'activity_type']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


@admin.register(UserAnalytics)
class UserAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_activities', 'total_exams_taken', 'average_exam_score', 'last_calculated_at']
    list_filter = ['last_calculated_at']
    search_fields = ['user__email']
    readonly_fields = ['last_calculated_at']
