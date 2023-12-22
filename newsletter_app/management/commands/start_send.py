import time
from django.core.management import BaseCommand
from datetime import date
from newsletter_app.models import Newsletter


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('StartSend')
        now = date.today()
        receivers = Newsletter.objects.filter(date_start__lte=now)
        receivers_list = [newsletter for newsletter in receivers if newsletter.status_send == 'CREATED']
        for newsletter in receivers_list:
            owner = newsletter.owner
            # newsletter.status_send = 'STARTED'
            # newsletter.save()
            mail_list = [mail.email for mail in newsletter.client.all()]
            print(mail_list)
            print(newsletter.status_send)
            print(owner)
            newsletter.status_send = 'CREATED'
            newsletter.save()
            print(newsletter.status_send)
            print(newsletter.message.subject)
            time.sleep(1.0)
            print(newsletter.message.text)
            print('---------')

