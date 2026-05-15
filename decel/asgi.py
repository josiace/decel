"""
ASGI config for DECEL project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'decel.settings')

application = get_asgi_application()
