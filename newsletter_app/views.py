from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from newsletter_app.models import Client, Newsletter, Options
from newsletter_app.forms import ClientForm, NewsletterForm, OptionsForm
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import inlineformset_factory


# Create your views here.
class ClientView(LoginRequiredMixin, ListView):
    model = Client
    extra_context = {'title': 'Список клиентов'}

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset()
        # queryset = queryset.filter(owner_id=self.kwargs.get('pk'), )
        if (not self.request.user.is_staff and not self.request.user.is_superuser
                and not self.request.user.groups.filter(name='moderators')):
            queryset = queryset.filter(owner=self.request.user)
        print(self.request.user.is_staff)
        print(self.request.user.is_superuser)
        print(self.request.user.pk)
        print(queryset)
        return queryset

    # def get_context_data(self, *, object_list=None, **kwargs):
    #     context_data = super().get_context_data(**kwargs)
    #     context_data['object_list'] = Client.objects.all()
    #     print(context_data['object_list'])
    #     return context_data


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


class NewsletterView(ListView):
    model = Newsletter

    def get_context_data(self, *, object_list=None, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['newsletter_list'] = Newsletter.objects.all()
        print(Newsletter.objects.all())
        return context_data


class NewsletterCreateView(CreateView):
    model = Newsletter
    form_class = NewsletterForm

    def get_success_url(self):
        return reverse_lazy('news:newsletter_detail', args=[self.object.pk])

    def form_valid(self, form):
        self.object = form.save()
        self.object.owner = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(NewsletterCreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user  # Передаем текущего пользователя в форму
        return kwargs


class NewsletterUpdateView(UpdateView):
    model = Newsletter
    form_class = NewsletterForm

    def get_success_url(self):
        return reverse_lazy('news:newsletter_detail', args=[self.object.pk])

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        OptionsFormset = inlineformset_factory(Newsletter, Options, form=OptionsForm, extra=1)
        if self.request.method == 'POST':
            context_data['formset'] = OptionsFormset(self.request.POST, instance=self.object)
        else:
            context_data['formset'] = OptionsFormset(instance=self.object)
        return context_data

    def form_valid(self, form):
        formset = self.get_context_data()['formset']
        self.object = form.save()
        if formset.is_valid():
            formset.instance = self.object
            formset.save()
        return super().form_valid(form)


class NewsletterDetailView(DetailView):
    model = Newsletter
    extra_context = {'title': 'Детали рассылки'}


class NewsletterDeleteView(DeleteView):
    model = Newsletter
    success_url = reverse_lazy('news:newsletters')

    def get_context_data(self, **kwargs):
        """Подтверждение удаления"""
        context_data = super().get_context_data(**kwargs)
        newsletter_item = Newsletter.objects.get(pk=self.kwargs.get('pk'))
        context_data['newsletter_pk'] = newsletter_item.pk
        context_data['title'] = f'Удаление рассылки {newsletter_item}'
        return context_data
