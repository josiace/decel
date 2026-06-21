"""
URL configuration for DECEL project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def home(request):
    """Landing page for DECEL - redirects to home_authenticated if user is logged in."""
    if request.user.is_authenticated:
        return redirect('home_authenticated')
    return render(request, 'home.html')

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('exams/', include('exams.urls')),
    path('learning/', include('learning.urls')),
    path('community/', include('community.urls')),
    path('contributor/', include('contributor.urls')),
    path('gamification/', include('gamification.urls')),
    path('analytics/', include('analytics.urls')),
    path('payments/', include('payments.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
