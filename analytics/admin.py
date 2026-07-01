from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html
from .models import UserActivity, UserAnalytics, PageView, ClickEvent, UserSession


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ['user', 'url', 'page_title', 'session_id', 'device_type', 'country', 'created_at']
    list_filter = ['device_type', 'browser', 'country', 'created_at']
    search_fields = ['user__email', 'url', 'page_title', 'session_id']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']


@admin.register(ClickEvent)
class ClickEventAdmin(admin.ModelAdmin):
    list_display = ['user', 'element_text', 'element_id', 'page_url', 'x_position', 'y_position', 'created_at']
    list_filter = ['element_tag', 'created_at']
    search_fields = ['user__email', 'element_text', 'element_id', 'page_url']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'session_id', 'page_views_count', 'unique_pages_count', 'duration_seconds', 'device_type', 'country', 'start_time']
    list_filter = ['device_type', 'is_completed', 'country', 'start_time']
    search_fields = ['user__email', 'session_id', 'entry_page', 'exit_page']
    readonly_fields = ['start_time', 'end_time', 'journey_path']
    date_hierarchy = 'start_time'
    ordering = ['-start_time']

    def duration_display(self, obj):
        if obj.duration_seconds:
            minutes = obj.duration_seconds // 60
            seconds = obj.duration_seconds % 60
            return f"{minutes}m {seconds}s"
        return "-"
    duration_display.short_description = "Durée"


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_type', 'created_at', 'ip_address']
    list_filter = ['activity_type', 'created_at']
    search_fields = ['user__email', 'activity_type']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


@admin.register(UserAnalytics)
class UserAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_activities', 'total_exams_taken', 'exams_passed', 'average_exam_score', 'total_time_spent_minutes', 'last_calculated_at']
    list_filter = ['last_calculated_at', 'most_active_subject']
    search_fields = ['user__email']
    readonly_fields = ['last_calculated_at']

    def average_exam_score_display(self, obj):
        if obj.average_exam_score:
            return f"{obj.average_exam_score}%"
        return "-"
    average_exam_score_display.short_description = "Score moyen"
