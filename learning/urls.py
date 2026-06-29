from django.urls import path
from . import views

urlpatterns = [
    path('courses/', views.course_list, name='course_list'),
    path('courses/create/', views.course_create, name='course_create'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('courses/<int:course_id>/update/', views.course_update, name='course_update'),
    path('courses/<int:course_id>/complete/', views.course_complete, name='course_complete'),
    path('courses/<int:course_id>/purchase/', views.purchase_course, name='purchase_course'),
    path('tds/', views.td_list, name='td_list'),
    path('tds/create/', views.td_create, name='td_create'),
    path('tds/<int:td_id>/', views.td_detail, name='td_detail'),
    path('tds/<int:td_id>/update/', views.td_update, name='td_update'),
    path('tds/<int:td_id>/complete/', views.td_complete, name='td_complete'),
    path('tds/<int:td_id>/purchase/', views.purchase_td, name='purchase_td'),
    path('corrections/<int:correction_id>/purchase/', views.purchase_correction, name='purchase_correction'),
    path('corrected-tds/create/', views.corrected_td_create, name='corrected_td_create'),
    path('corrected-tds/<int:corrected_td_id>/update/', views.corrected_td_update, name='corrected_td_update'),
    path('download/<str:content_type>/<int:content_id>/', views.download_file, name='download_file'),
    path('versions/<str:content_type>/<int:content_id>/', views.content_version_history, name='content_version_history'),
    path('versions/<str:content_type>/<int:content_id>/restore/<int:version_number>/', views.restore_content_version, name='restore_content_version'),
    path('review/submit/', views.submit_review, name='submit_review'),
]
