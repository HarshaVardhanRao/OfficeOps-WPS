import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'office_ops.settings')

app = Celery('office_ops')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
