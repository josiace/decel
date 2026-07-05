web: gunicorn decel.wsgi:application
release: python manage.py migrate && python manage.py collectstatic --noinput
