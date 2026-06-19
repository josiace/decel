from django.urls import path
from . import views

app_name = 'gamification'

urlpatterns = [
    path('leaderboards/', views.leaderboard_list, name='leaderboard_list'),
    path('leaderboards/<int:leaderboard_id>/', views.leaderboard_detail, name='leaderboard_detail'),
    path('leaderboard/global/', views.global_leaderboard, name='global_leaderboard'),
    path('leaderboard/subject/<int:subject_id>/', views.subject_leaderboard, name='subject_leaderboard'),
]
