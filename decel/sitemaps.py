"""Sitemaps XML pour le référencement."""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from exams.models import Exam
from learning.models import Course, TD
from skills.models import Subject


class StaticViewSitemap(Sitemap):
    """Pages publiques indexables."""

    protocol = 'https'

    def items(self):
        return [
            ('home', 1.0, 'daily'),
            ('register', 0.8, 'monthly'),
            ('login', 0.5, 'monthly'),
        ]

    def location(self, item):
        return reverse(item[0])

    def priority(self, item):
        return item[1]

    def changefreq(self, item):
        return item[2]


class ExamSitemap(Sitemap):
    """Sitemap pour les examens publics."""
    protocol = 'https'
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Exam.objects.filter(is_active=True).select_related('subject')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('exam_detail', args=[obj.id])


class CourseSitemap(Sitemap):
    """Sitemap pour les cours publiés."""
    protocol = 'https'
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Course.objects.filter(is_published=True).select_related('subject')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('course_detail', args=[obj.id])


class TDSitemap(Sitemap):
    """Sitemap pour les TD publiés."""
    protocol = 'https'
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return TD.objects.filter(is_published=True).select_related('subject')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('td_detail', args=[obj.id])


class SubjectSitemap(Sitemap):
    """Sitemap pour les matières."""
    protocol = 'https'
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return Subject.objects.all()

    def lastmod(self, obj):
        return obj.created_at

    def location(self, obj):
        return f'/subjects/{obj.id}/'
