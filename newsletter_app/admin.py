from django.contrib import admin
from newsletter_app.models import Client, Newsletter, Message, Logs

# Register your models here.
admin.site.register(Client)
admin.site.register(Newsletter)
admin.site.register(Message)
admin.site.register(Logs)
