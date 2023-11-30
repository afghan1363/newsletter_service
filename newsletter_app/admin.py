from django.contrib import admin
from newsletter_app.models import Client, Message, Newsletter, Logs

# Register your models here.
admin.site.register(Client)
admin.site.register(Message)
admin.site.register(Newsletter)
admin.site.register(Logs)
