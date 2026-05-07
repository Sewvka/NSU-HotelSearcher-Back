celery -A tasks.tasks worker --loglevel=INFO -P solo

celery -A tasks.tasks beat