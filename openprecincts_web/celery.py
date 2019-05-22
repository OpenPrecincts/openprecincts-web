import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "openprecincts_web.settings")

app = Celery("openprecincts_web")
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
