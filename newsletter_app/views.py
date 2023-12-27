from django.contrib.auth.decorators import login_required, permission_required
from django.http import request
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from newsletter_app.models import Client, Newsletter, Message, Logs
from newsletter_app.forms import ClientForm, NewsletterForm, MessageForm
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.forms import inlineformset_factory
from users.models import User


# Create your views here.
class ClientView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Client
    permission_required = ('newsletter_app.view_client',)

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset()
        # queryset = queryset.filter(owner_id=self.kwargs.get('pk'), )

        if self.request.user.groups.filter(name='Moderators'):
            self.model = User
            # self.permission_required = ('users.change_user',)
            self.template_name = 'users/user_list.html'
        # elif not self.request.user.is_staff and not self.request.user.is_superuser:
        else:
            queryset = queryset.filter(owner=self.request.user)
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context_data = super().get_context_data(**kwargs)
        current_user = self.request.user
        context_data['title'] = 'Список клиентов'
        if self.request.user.groups.filter(name='Moderators'):
            context_data['object_list'] = User.objects.exclude(email=current_user)
            context_data['object_list'] = context_data['object_list'].exclude(is_superuser=True).order_by('email')
            context_data['title'] = 'Список пользователей'
        return context_data


class ClientCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    success_url = reverse_lazy('news:index')
    permission_required = ('newsletter_app.add_client',)

    def form_valid(self, form):
        self.object = form.save()
        self.object.owner = self.request.user
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    permission_required = ('newsletter_app.change_client',)

    def get_success_url(self):
        return reverse_lazy('news:client', args=[self.object.pk])


class ClientDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Client
    permission_required = ('newsletter_app.view_client',)


class ClientDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Client
    success_url = reverse_lazy('news:index')
    permission_required = ('newsletter_app.delete_client',)

    def get_context_data(self, **kwargs):
        """Подтверждение удаления"""
        context_data = super().get_context_data(**kwargs)
        client_item = Client.objects.get(pk=self.kwargs.get('pk'))
        context_data['client_pk'] = client_item.pk
        context_data['title'] = f'Удаление клиента {client_item}'
        return context_data


class NewsletterView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Newsletter
    permission_required = ('newsletter_app.view_newsletter',)
    extra_context = {'title': 'Рассылки'}

    def get_queryset(self):
        queryset = super().get_queryset()
        if (not self.request.user.is_staff and not self.request.user.is_superuser
                and not self.request.user.groups.filter(name='Moderators')):
            queryset = queryset.filter(owner=self.request.user)
        return queryset


class NewsletterCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Newsletter
    form_class = NewsletterForm
    permission_required = ('newsletter_app.add_newsletter',)

    def get_success_url(self):
        return reverse_lazy('news:newsletter_detail', args=[self.object.pk])

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.save()
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(NewsletterCreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user  # Передаю текущего пользователя в форму
        return kwargs


class NewsletterUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Newsletter
    form_class = NewsletterForm
    permission_required = ('newsletter_app.change_newsletter',)

    def get_success_url(self):
        return reverse_lazy('news:newsletter_detail', args=[self.object.pk])

    def get_form_kwargs(self):
        kwargs = super(NewsletterUpdateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user  # Передаем текущего пользователя в форму
        return kwargs

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        options_formset = inlineformset_factory(Newsletter, Message, form=MessageForm, extra=1, max_num=1,
                                                validate_max=True)
        if self.request.method == 'POST':
            context_data['formset'] = options_formset(self.request.POST, instance=self.object)
        else:
            context_data['formset'] = options_formset(instance=self.object)
        return context_data

    def form_valid(self, form):
        formset = self.get_context_data()['formset']
        self.object = form.save()
        if formset.is_valid():
            formset.instance = self.object
            print(formset.instance)
            formset.save()
        return super().form_valid(form)


@login_required
@permission_required(perm='newsletter_app.set_status_send', login_url='users:login')
def change_newsletter_status(request, pk):
    """
    Переключение статуса рассылки
    :param request: реквест
    :param pk: пикей рассылки
    :return: redirect
    """
    newsletter_item = get_object_or_404(Newsletter, pk=pk)
    if newsletter_item.status_send != 'COMPLETED':
        newsletter_item.status_send = 'COMPLETED'
    else:
        newsletter_item.status_send = 'CREATED'
    newsletter_item.save()
    return redirect(reverse('newsletter_app:newsletters'))


class NewsletterDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Newsletter
    extra_context = {'title': 'Детали рассылки'}
    permission_required = ('newsletter_app.view_newsletter',)


class NewsletterDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Newsletter
    success_url = reverse_lazy('news:newsletters')
    permission_required = ('newsletter_app.delete_newsletter',)

    def get_context_data(self, **kwargs):
        """
        Подтверждение удаления
        """
        context_data = super().get_context_data(**kwargs)
        newsletter_item = Newsletter.objects.get(pk=self.kwargs.get('pk'))
        context_data['newsletter_pk'] = newsletter_item.pk
        context_data['title'] = f'Удаление рассылки {newsletter_item}'
        return context_data


class LogsView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Newsletter
    template_name = 'newsletter_app/logs_list.html'
    permission_required = 'newsletter_app.view_logs'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(owner=self.request.user)
        return queryset
