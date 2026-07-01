from django.urls import path
from . import views

app_name = 'b2b'

urlpatterns = [
    path('partners/', views.partner_list, name='partner_list'),
    path('partners/<int:partner_id>/', views.partner_detail, name='partner_detail'),
    path('partners/create/', views.create_partner, name='create_partner'),
    path('licenses/', views.license_list, name='license_list'),
    path('licenses/<int:license_id>/', views.license_detail, name='license_detail'),
    path('licenses/create/<int:partner_id>/', views.create_license, name='create_license'),
    path('licenses/<int:license_id>/add-user/', views.add_user_to_license, name='add_user'),
    path('licenses/<int:license_id>/remove-user/<int:user_id>/', views.remove_user_from_license, name='remove_user'),
    path('licenses/<int:license_id>/renew/', views.renew_license, name='renew'),
    path('licenses/<int:license_id>/upgrade/', views.upgrade_license, name='upgrade'),
]
