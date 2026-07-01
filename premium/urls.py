from django.urls import path
from . import views

app_name = 'premium'

urlpatterns = [
    path('', views.service_list, name='list'),
    path('service/<int:service_id>/', views.service_detail, name='detail'),
    path('service/<int:service_id>/book/', views.book_service, name='book'),
    path('booking/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('my-services/', views.my_services, name='my_services'),
    path('create/', views.create_service, name='create'),
    path('booking/<int:booking_id>/confirm/', views.confirm_booking, name='confirm'),
    path('booking/<int:booking_id>/start/', views.start_session, name='start'),
    path('booking/<int:booking_id>/complete/', views.complete_session, name='complete'),
    path('booking/<int:booking_id>/cancel/', views.cancel_booking, name='cancel'),
    path('booking/<int:booking_id>/review/', views.submit_review, name='review'),
]
