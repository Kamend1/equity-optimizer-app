web: gunicorn EquityOptimizerApp.wsgi --workers=3 --timeout=1200
worker: celery -A EquityOptimizerApp worker --loglevel=info
beat: celery -A EquityOptimizerApp beat --scheduler django_celery_beat.schedulers:DatabaseScheduler --loglevel=info