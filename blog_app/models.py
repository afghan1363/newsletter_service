from django.db import models
from newsletter_app.models import NULLABLE, get_date_now


# Create your models here.
class Blog(models.Model):
    title = models.CharField(max_length=500, verbose_name='Заголовок')
    body = models.TextField(verbose_name='Текст блога')
    image = models.ImageField(verbose_name='Изображение', **NULLABLE)
    views = models.IntegerField(verbose_name='Количество просмотров', **NULLABLE)
    published_date = models.DateField(default=get_date_now, verbose_name='Дата публикации')
