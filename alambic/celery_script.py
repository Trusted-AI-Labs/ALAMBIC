import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alambic.settings')

app = Celery('alambic')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

if __name__ == "__main__":
    worker = app.Worker(pool = "solo", loglevel = "INFO")
    worker.start()
