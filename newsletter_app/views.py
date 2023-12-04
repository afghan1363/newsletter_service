from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from newsletter_app.models import Client
from newsletter_app.forms import ClientForm
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin


# Create your views here.
class ClientView(LoginRequiredMixin, ListView):
    model = Client
    extra_context = {'title': 'Список клиентов'}

    def get_context_data(self, *, object_list=None, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['client_list'] = Client.objects.all()
        return context_data

    def get_queryset(self):
        queryset = super().get_queryset()

        return queryset


class ClientCreateView(CreateView):
    model = Client
    form_class = ClientForm
    success_url = reverse_lazy('news:index')

    def form_valid(self, form):
        self.object = form.save()
        self.object.user = self.request.user
        return super().form_valid(form)


class ClientUpdateView(UpdateView):
    model = Client
    form_class = ClientForm

    def get_success_url(self):
        return reverse_lazy('news:client', args=[self.object.pk])


class ClientDetailView(DetailView):
    model = Client

class ClientDeleteView(DeleteView):
    model = Client
    success_url = reverse_lazy('news:index')

    def get_context_data(self, **kwargs):
        """Подтверждение удаления"""
        context_data = super().get_context_data(**kwargs)
        client_item = Client.objects.get(pk=self.kwargs.get('pk'))
        context_data['client_pk'] = client_item.pk
        context_data['title'] = f'Удаление клиента {client_item}'
        return context_data
