from django.db import models
from django.conf import settings
from datetime import date, timedelta


# Create your models here.
def get_date_now():
    """Получение текущей даты"""
    return date.today()


def get_date_plus_week():
    """Получение даты через неделю"""
    return date.today() + timedelta(weeks=1)


NULLABLE = {'blank': True, 'null': True}


class Client(models.Model):
    email = models.EmailField(verbose_name='Почта')
    full_name = models.CharField(max_length=150, verbose_name='ФИО')
    comment = models.TextField(verbose_name='Комментарий')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, **NULLABLE,
                              verbose_name='Менеджер клиента')

    def __str__(self):
        return f'{self.full_name} ({self.email})'

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'


class Message(models.Model):
    subject = models.CharField(max_length=100, verbose_name='Тема сообщения', blank=True)
    text = models.TextField(verbose_name='Текст сообщения', blank=True)
    newsletter = models.OneToOneField('Newsletter', on_delete=models.CASCADE, verbose_name='Рассылка')

    def __str__(self):
        return f'{self.subject}'

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'


class Newsletter(models.Model):
    PERIODS_SEND = (
        ('DAILY', 'Раз в день'),
        ('WEEKLY', 'Раз в неделю'),
        ('MONTHLY', 'Раз в месяц'),
    )

    STATUSES_SEND = (
        ('CREATED', 'Создана'),
        ('STARTED', 'Запущена'),
        ('COMPLETED', 'Завершена'),
    )

    client = models.ManyToManyField(Client, verbose_name='Клиент')
    date_start = models.DateField(default=get_date_now, verbose_name='Дата старта рассылки')
    date_stop = models.DateField(default=get_date_plus_week, verbose_name='Дата завершение рассылки')
    period_send = models.CharField(max_length=20, choices=PERIODS_SEND, default='WEEKLY', verbose_name='Периодичность')
    status_send = models.CharField(max_length=20, choices=STATUSES_SEND, default='CREATED',
                                   verbose_name='Статус рассылки')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, **NULLABLE,
                              verbose_name='Менеджер клиента')

    def __str__(self):
        return f'Активна до {self.date_stop} - {self.period_send} - {self.status_send}'

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        permissions = [
            (
                'set_status_send',
                'Can change status_send'
            ),
        ]


class Logs(models.Model):
    time = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время попытки')
    status = models.CharField(max_length=10, verbose_name='Статус')
    mail_serv_response = models.TextField(verbose_name='Ответ почтового сервера')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Клиент')
    newsletter = models.ForeignKey(Newsletter, on_delete=models.CASCADE, verbose_name='Рассылка')

    def __str__(self):
        return f'Лог: {self.time}'

    class Meta:
        verbose_name = 'Лог'
        verbose_name_plural = 'Логи'
