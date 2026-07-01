"""
URL configuration for DECEL project.
"""
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render, redirect
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView

from decel.sitemaps import StaticViewSitemap, ExamSitemap, CourseSitemap, TDSitemap, SubjectSitemap, CorrectedTDSitemap, BlogSitemap
from decel.seo_views import robots_txt

sitemaps = {
    'static': StaticViewSitemap,
    'exams': ExamSitemap,
    'courses': CourseSitemap,
    'tds': TDSitemap,
    'corrected_tds': CorrectedTDSitemap,
    'subjects': SubjectSitemap,
    'blog': BlogSitemap,
}

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
    path('robots.txt', robots_txt, name='robots_txt'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path(
        'manifest.webmanifest',
        TemplateView.as_view(
            template_name='manifest.webmanifest',
            content_type='application/manifest+json',
        ),
        name='manifest',
    ),
    path('', include('accounts.urls')),
    path('exams/', include('exams.urls')),
    path('learning/', include('learning.urls')),
    path('community/', include('community.urls')),
    path('contributor/', include('contributor.urls')),
    path('gamification/', include('gamification.urls')),
    path('analytics/', include('analytics.urls')),
    path('payments/', include('payments.urls')),
    path('api/', include('api.urls')),
    path('subscriptions/', include('subscriptions.urls')),
    path('premium/', include('premium.urls')),
    path('b2b/', include('b2b.urls')),
    path('blog/', include('blog.urls')),
]

# Set custom error handlers
handler404 = custom_404
handler403 = custom_403
handler500 = custom_500
handler400 = custom_400

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
