from celery import shared_task
from django.core.mail import send_mail
import os

@shared_task
def send_email_async(subject, message, from_email, recipient_list):
    print("SSL keyfile:", os.environ.get("EMAIL_SSL_KEYFILE"))
    print("SSL certfile:", os.environ.get("EMAIL_SSL_CERTFILE"))

    send_mail(subject, message, from_email, recipient_list)
