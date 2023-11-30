from django.urls import path
from newsletter_app.apps import NewsletterAppConfig
from newsletter_app.views import IndexView

app_name = NewsletterAppConfig.name

urlpatterns = [
    path('', IndexView.as_view(), name='index')
]
