"""
WSGI config for DECEL project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'decel.settings')

application = get_wsgi_application()
