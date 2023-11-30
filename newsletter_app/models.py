from django.db import models
from django.conf import settings

# Create your models here.
NULLABLE = {'blank': True, 'null': True}

PERIODS_SEND = (
    ('day', 'Раз в день'),
    ('week', 'Раз в неделю'),
    ('month', 'Раз в месяц'),
)

STATUSES_SEND = (
    ('created', 'Создана'),
    ('started', 'Запущена'),
    ('completed', 'Завершена'),
)


class Client(models.Model):
    email = models.EmailField(verbose_name='Почта')
    full_name = models.CharField(max_length=150, verbose_name='ФИО')
    comment = models.TextField(verbose_name='Комментарий')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, **NULLABLE,
                             verbose_name='Менеджер клиента')

    def __str__(self):
        return f'{self.full_name} ({self.email})'

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'


class Message(models.Model):
    subject = models.CharField(max_length=100, verbose_name='Тема сообщения')
    text = models.TextField(verbose_name='Текст сообщения')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, **NULLABLE,
                             verbose_name='Менеджер клиента')

    def __str__(self):
        return self.subject

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'


class Newsletter(models.Model):
    time_send = models.TimeField(verbose_name='Время рассылки')
    date_send = models.DateField(verbose_name='Дата рассылки', **NULLABLE)
    period_send = models.CharField(max_length=20, choices=PERIODS_SEND, default='week', verbose_name='Периодичность')
    status_send = models.CharField(max_length=20, choices=STATUSES_SEND, verbose_name='Статус рассылки')
    client = models.ManyToManyField(Client, verbose_name='Клиент')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, verbose_name='Сообщение')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, **NULLABLE,
                             verbose_name='Менеджер клиента')

    def __str__(self):
        return f'{self.time_send} - {self.status_send}'

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'


class Logs(models.Model):
    time = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время попытки')
    status = models.CharField(max_length=10, verbose_name='Статус')
    mail_serv_response = models.TextField(verbose_name='Ответ почтового сервера')
    newsletter = models.ForeignKey(Newsletter, on_delete=models.SET_NULL, verbose_name='Рассылка', **NULLABLE)

    def __str__(self):
        return f'Лог: {self.time}'

    class Meta:
        verbose_name = 'Лог'
        verbose_name_plural = 'Логи'