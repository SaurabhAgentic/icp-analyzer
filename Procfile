web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 4 --threads 2 --timeout 120
worker: celery -A src.core.tasks worker --loglevel=info 