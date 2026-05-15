from django.urls import path
from . import views

urlpatterns = [
    path('', views.exam_list, name='exam_list'),
    path('<int:exam_id>/', views.exam_detail, name='exam_detail'),
    path('<int:exam_id>/take/', views.exam_take, name='exam_take'),
    path('<int:exam_id>/submit/', views.exam_submit, name='exam_submit'),
    path('result/<int:session_id>/', views.exam_result, name='exam_result'),
]
