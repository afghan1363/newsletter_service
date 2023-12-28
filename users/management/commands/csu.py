from django.core.management import BaseCommand
from users.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        email = input('email: ')
        first_name = input('first_name: ')
        last_name = input('last_name: ')
        password = input('password: ')
        user = User.objects.create(
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_superuser=True,
            is_staff=True,
            is_active=True
        )
        user.set_password(password)
        user.save()
