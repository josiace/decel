from django.urls import path
from . import views

urlpatterns = [
    path('', views.content_list, name='content_list'),
    path('<int:content_id>/', views.content_detail, name='content_detail'),
    path('my-content/', views.my_content, name='my_content'),
    path('create/', views.content_create, name='content_create'),
    path('edit/<int:content_id>/', views.content_edit, name='content_edit'),
    path('submit/<int:content_id>/', views.content_submit, name='content_submit'),
    path('purchase/<int:content_id>/', views.purchase_content, name='purchase_content'),
    path('download/<int:content_id>/', views.download_file, name='download_file'),
    path('moderation/', views.moderation_queue, name='moderation_queue'),
    path('moderate/<int:content_id>/', views.moderate_content, name='moderate_content'),
]
