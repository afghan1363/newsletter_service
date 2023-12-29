from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
import smtplib
import time
from datetime import date, datetime, timedelta

from blog_app.models import Blog
from newsletter_app.models import Newsletter, Logs
from calendar import monthrange


def mailing_util(subject,
                 message,
                 recipient_list,
                 from_email=settings.EMAIL_HOST_USER
                 ):
    try:
        status_send = send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list
        )
        return status_send
    except smtplib.SMTPException:
        raise smtplib.SMTPException


def do_newsletter():
    """
    Функция отправки сообщений
    :return:
    """
    print('StartSend')
    now = date.today()
    receivers = Newsletter.objects.filter(date_start__lte=now, date_stop__gte=now)
    new_receivers_list = [newsletter for newsletter in receivers if newsletter.status_send == 'CREATED']
    if len(new_receivers_list) > 0:
        for newsletter in new_receivers_list:
            newsletter.status_send = 'STARTED'
            newsletter.save()
    receivers_list = [newsletter for newsletter in receivers if newsletter.status_send == 'STARTED']
    if len(receivers_list) > 0:
        for newsletter in receivers_list:
            mail_list = [client.email for client in newsletter.client.all()]
            subject = newsletter.message.subject
            message = newsletter.message.text
            recipient_list = mail_list
            try:
                status_send = mailing_util(subject=subject, message=message, recipient_list=recipient_list)
                for client in newsletter.client.all():
                    log = Logs.objects.create(
                        time=datetime.now(), status=bool(status_send), mail_serv_response='</>',
                        client=client, newsletter=newsletter)
                if newsletter.date_stop == now:
                    newsletter.status_send = 'COMPLETED'
                elif newsletter.period_send == 'DAILY':
                    newsletter.date_start += timedelta(days=1)
                elif newsletter.period_send == 'WEEKLY':
                    newsletter.date_start += timedelta(weeks=1)
                elif newsletter.period_send == 'MONTHLY':
                    month = now.month
                    year = now.year
                    days_count = monthrange(year, month)
                    newsletter.date_start += timedelta(days=days_count[1])
            except smtplib.SMTPException as error:
                for client in newsletter.client.all():
                    log = Logs.objects.create(
                        time=datetime.now(), status=bool(status_send), mail_serv_response=error,
                        client=client, newsletter=newsletter)
            finally:
                log.save()
                newsletter.save()
    print('EndSend')


def cache_it():
    """Кэширование блога"""
    if settings.CACHE_ENABLED:
        key = 'blog_list'
        blog_list = cache.get(key)
        if blog_list is None:
            blog_list = Blog.objects.all()
            cache.set(key, blog_list)
    else:
        blog_list = Blog.objects.all()
        return blog_list
