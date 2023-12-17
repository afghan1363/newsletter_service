import datetime
from django.db import models
from django.conf import settings
from datetime import date


# Create your models here.
def get_date_now():
    return date.today()


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
    # owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, **NULLABLE,
    #                           verbose_name='Менеджер клиента')

    def __str__(self):
        return f'{self.subject}'

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'


class Newsletter(models.Model):
    DAILY = 'day'
    WEEKLY = 'week'
    MONTHLY = 'month'
    PERIODS_SEND = (
        (DAILY, 'Раз в день'),
        (WEEKLY, 'Раз в неделю'),
        (MONTHLY, 'Раз в месяц'),
    )

    CREATED = 'crtd'
    STARTED = 'strtd'
    COMPLETED = 'cmpld'
    STATUSES_SEND = (
        (CREATED, 'Создана'),
        (STARTED, 'Запущена'),
        (COMPLETED, 'Завершена'),
    )

    client = models.ManyToManyField(Client, verbose_name='Клиент')
    date_start = models.DateField(default=get_date_now, verbose_name='Время рассылки')
    period_send = models.CharField(max_length=20, choices=PERIODS_SEND, default=WEEKLY, verbose_name='Периодичность')
    status_send = models.CharField(max_length=20, choices=STATUSES_SEND, default=CREATED,
                                   verbose_name='Статус рассылки')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              verbose_name='Менеджер клиента')

    def __str__(self):
        return f'{self.date_start} - {self.status_send}'

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'


class Logs(models.Model):
    time = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время попытки')
    status = models.CharField(max_length=10, verbose_name='Статус')
    mail_serv_response = models.TextField(verbose_name='Ответ почтового сервера')
    # newsletter = models.ForeignKey(Newsletter, on_delete=models.SET_NULL, verbose_name='Рассылка', **NULLABLE)
    # owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, **NULLABLE,
    #                           verbose_name='Менеджер клиента')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='')
    newsletter = models.ForeignKey(Newsletter, on_delete=models.CASCADE, verbose_name='Рассылка')

    def __str__(self):
        return f'Лог: {self.time}'

    class Meta:
        verbose_name = 'Лог'
        verbose_name_plural = 'Логи'
