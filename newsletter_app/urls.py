from django.urls import path
from django.views.decorators.cache import cache_page

from newsletter_app.apps import NewsletterAppConfig
from newsletter_app.views import (StartPageView, ClientView, ClientCreateView, ClientUpdateView, ClientDetailView, ClientDeleteView,
                                  NewsletterView, NewsletterCreateView, NewsletterDetailView, NewsletterUpdateView,
                                  NewsletterDeleteView, LogsView, change_newsletter_status)

app_name = NewsletterAppConfig.name

urlpatterns = [
    path('', cache_page(60)(StartPageView.as_view()), name='start_page'),
    path('index/', ClientView.as_view(), name='index'),
    path('new_client/', ClientCreateView.as_view(), name='create_client'),
    path('update_client/<int:pk>', ClientUpdateView.as_view(), name='update_client'),
    path('client/<int:pk>', ClientDetailView.as_view(), name='client'),
    path('delete_client/<int:pk>', ClientDeleteView.as_view(), name='delete_client'),
    path('newsletters/', NewsletterView.as_view(), name='newsletters'),
    path('newsletter/create/', NewsletterCreateView.as_view(), name='create_newsletter'),
    path('newsletter/<int:pk>/', NewsletterDetailView.as_view(), name='newsletter_detail'),
    path('newsletter/<int:pk>/update', NewsletterUpdateView.as_view(), name='update_newsletter'),
    path('newsletter/<int:pk>/delete', NewsletterDeleteView.as_view(), name='delete_newsletter'),
    path('logs/', LogsView.as_view(), name='logs'),
    path('newsletter_status/<int:pk>/', change_newsletter_status, name='newsletter_status'),
]
