"""Sitemaps XML pour le référencement."""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse


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
