from django.core.mail import send_mail
from django.conf import settings


def send_newsletter_job():
    send_mail(
        subject='Верификация SkyStore',
        message=f'''Перейдите по ссылке для верификации: http://127.0.0.1:8000/users/verification_code/
    и введите Логин и пароль''',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=['maksim_abavi@vk.ru']
    )
