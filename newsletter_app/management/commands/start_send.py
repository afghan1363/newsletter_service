from django.core.management import BaseCommand
from newsletter_app.services import do_newsletter


class Command(BaseCommand):
    def handle(self, *args, **options):
        do_newsletter()

