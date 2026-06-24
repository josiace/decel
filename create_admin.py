import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'decel.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '')
first_name = os.environ.get('DJANGO_SUPERUSER_FIRST_NAME', 'Admin')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        first_name=first_name
    )
    print(f"Superuser '{username}' créé.")
else:
    print(f"Superuser '{username}' existe déjà.")