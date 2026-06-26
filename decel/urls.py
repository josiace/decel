"""
URL configuration for DECEL project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

@cache_page(60 * 10)  # 10 minutes
def home(request):
    """Landing page for DECEL - redirects to home_authenticated if user is logged in."""
    if request.user.is_authenticated:
        return redirect('home_authenticated')
    return render(request, 'home.html')

# Custom error handlers
def custom_404(request, exception):
    """Custom 404 error handler."""
    return render(request, 'errors/404.html', status=404)

def custom_403(request, exception):
    """Custom 403 error handler."""
    return render(request, 'errors/403.html', status=403)

def custom_500(request):
    """Custom 500 error handler."""
    return render(request, 'errors/500.html', status=500)

def custom_400(request, exception):
    """Custom 400 error handler."""
    return render(request, 'errors/400.html', status=400)

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
    path('api/', include('api.urls')),
]

# Set custom error handlers
handler404 = custom_404
handler403 = custom_403
handler500 = custom_500
handler400 = custom_400

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
