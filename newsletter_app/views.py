from django.shortcuts import render
from django.views.generic import ListView
from newsletter_app.models import Client


# Create your views here.
class IndexView(ListView):
    model = Client
