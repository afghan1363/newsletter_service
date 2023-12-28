# Generated by Django 4.2.7 on 2023-12-17 11:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import newsletter_app.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, verbose_name='Почта')),
                ('full_name', models.CharField(max_length=150, verbose_name='ФИО')),
                ('comment', models.TextField(verbose_name='Комментарий')),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Менеджер клиента')),
            ],
            options={
                'verbose_name': 'Клиент',
                'verbose_name_plural': 'Клиенты',
            },
        ),
        migrations.CreateModel(
            name='Newsletter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_start', models.DateField(default=newsletter_app.models.get_date_now, verbose_name='Время рассылки')),
                ('period_send', models.CharField(choices=[('day', 'Раз в день'), ('week', 'Раз в неделю'), ('month', 'Раз в месяц')], default='week', max_length=20, verbose_name='Периодичность')),
                ('status_send', models.CharField(choices=[('crtd', 'Создана'), ('strtd', 'Запущена'), ('cmpld', 'Завершена')], default='crtd', max_length=20, verbose_name='Статус рассылки')),
                ('client', models.ManyToManyField(to='newsletter_app.client', verbose_name='Клиент')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Менеджер клиента')),
            ],
            options={
                'verbose_name': 'Рассылка',
                'verbose_name_plural': 'Рассылки',
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(blank=True, max_length=100, verbose_name='Тема сообщения')),
                ('text', models.TextField(blank=True, verbose_name='Текст сообщения')),
                ('newsletter', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='newsletter_app.newsletter', verbose_name='Рассылка')),
            ],
            options={
                'verbose_name': 'Сообщение',
                'verbose_name_plural': 'Сообщения',
            },
        ),
        migrations.CreateModel(
            name='Logs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(auto_now_add=True, verbose_name='Дата и время попытки')),
                ('status', models.CharField(max_length=10, verbose_name='Статус')),
                ('mail_serv_response', models.TextField(verbose_name='Ответ почтового сервера')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='newsletter_app.client', verbose_name='')),
                ('newsletter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='newsletter_app.newsletter', verbose_name='Рассылка')),
            ],
            options={
                'verbose_name': 'Лог',
                'verbose_name_plural': 'Логи',
            },
        ),
    ]
