# Generated by Django 4.2.7 on 2023-11-30 08:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsletter_app', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='newsletter',
            name='date_send',
            field=models.DateField(blank=True, null=True, verbose_name='Дата рассылки'),
        ),
    ]
