# Generated by Django 4.2.7 on 2023-12-05 15:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('newsletter_app', '0007_options_alter_newsletter_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='newsletter',
            options={'verbose_name': 'Рассылка', 'verbose_name_plural': 'Рассылки'},
        ),
        migrations.AlterModelOptions(
            name='options',
            options={'verbose_name': 'Настройка', 'verbose_name_plural': 'Настройки'},
        ),
    ]