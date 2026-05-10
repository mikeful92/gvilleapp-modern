release: python scripts/build_db.py && python manage.py collectstatic --noinput
web: gunicorn WebApp.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 4 --access-logfile -
