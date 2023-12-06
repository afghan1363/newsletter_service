from django.urls import path
from newsletter_app.apps import NewsletterAppConfig
from newsletter_app.views import (ClientView, ClientCreateView, ClientUpdateView, ClientDetailView, ClientDeleteView,
                                  NewsletterView, NewsletterCreateView, NewsletterDetailView)

app_name = NewsletterAppConfig.name

urlpatterns = [
    path('', ClientView.as_view(), name='index'),
    path('new_client/', ClientCreateView.as_view(), name='create_client'),
    path('update_client/<int:pk>', ClientUpdateView.as_view(), name='update_client'),
    path('client/<int:pk>', ClientDetailView.as_view(), name='client'),
    path('delete_client/<int:pk>', ClientDeleteView.as_view(), name='delete_client'),
    path('newsletters/', NewsletterView.as_view(), name='newsletters'),
    path('newsletter/create/', NewsletterCreateView.as_view(), name='create_newsletter'),
    path('newsletter/<int:pk>/', NewsletterDetailView.as_view(), name='newsletter_detail'),

]
