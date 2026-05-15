from django.urls import path
from . import views

app_name = 'contributor'

urlpatterns = [
    path('', views.contributor_dashboard, name='dashboard'),
    path('courses/', views.contributor_courses, name='courses'),
    path('exams/', views.contributor_exams, name='exams'),
    path('community/', views.contributor_community, name='community'),
    path('exam/create/', views.create_exam, name='create_exam'),
    path('exam/<int:exam_id>/edit/', views.edit_exam, name='edit_exam'),
    path('exam/<int:exam_id>/questions/', views.add_questions, name='add_questions'),
    path('exam/<int:exam_id>/question/<int:question_id>/delete/', views.delete_question, name='delete_question'),
]
