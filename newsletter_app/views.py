from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import (ListView, CreateView, UpdateView,
                                  DetailView, DeleteView, TemplateView)
from newsletter_app.models import Client, Newsletter, Message
from newsletter_app.forms import ClientForm, NewsletterForm, MessageForm
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.forms import inlineformset_factory
from newsletter_app.services import cache_it
from users.models import User
from random import shuffle


# Create your views here.
class StartPageView(LoginRequiredMixin, TemplateView):
    template_name = 'newsletter_app/start_page.html'

    def get_context_data(self, **kwargs):
        """Вывод информации на главную страницу"""
        context_data = super().get_context_data(**kwargs)
        context_data['title'] = 'The NewsLetter Service'
        if not self.request.user.is_superuser:
            count_clients = len(Client.objects.filter(owner=self.request.user.pk))
            count_newsletters = len(Newsletter.objects.filter(owner=self.request.user.pk))
        else:
            count_clients = len(Client.objects.all())
            count_newsletters = len(Newsletter.objects.all())
        active_newsletters = len(Newsletter.objects.filter(owner=self.request.user.pk,
                                                           status_send='STARTED'))
        blog_items = cache_it()
        if blog_items:
            blog_list = [blog for blog in blog_items]
            shuffle(blog_list)
            random_blog_list = blog_list[:3]
            context_data['random_blog_list'] = random_blog_list
        context_data['count_clients'] = count_clients
        context_data['count_newsletters'] = count_newsletters
        context_data['active_newsletters'] = active_newsletters

        return context_data


class ClientView(LoginRequiredMixin, ListView, PermissionRequiredMixin):
    model = Client
    permission_required = ('newsletter_app.view_client',)

    def get_queryset(self, *args, **kwargs):
        """Переопределение модели и прав доступа для Модератора"""
        queryset = super().get_queryset()
        if self.request.user.groups.filter(name='Moderators'):
            self.model = User
            self.permission_required = ('users.set_is_active',)
            self.template_name = 'users/user_list.html'
        else:
            queryset = queryset.filter(owner=self.request.user)

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        """Формирование object_list в зависимости от группы пользователя"""
        context_data = super().get_context_data(**kwargs)
        current_user = self.request.user
        context_data['title'] = 'Список клиентов'
        if self.request.user.groups.filter(name='Moderators'):
            context_data['object_list'] = User.objects.exclude(email=current_user)
            context_data['object_list'] = context_data['object_list'].exclude(is_superuser=True).order_by('email')
            context_data['title'] = 'Список пользователей'
        # context_data = super().get_context_data(**kwargs)
        context_data['title'] = 'Список клиентов'
        count_clients = len(Client.objects.filter(owner=self.request.user.pk))
        count_newsletters = len(Newsletter.objects.filter(owner=self.request.user.pk))
        active_newsletters = len(Newsletter.objects.filter(owner=self.request.user.pk, status_send='STARTED'))
        context_data['count_clients'] = count_clients
        context_data['count_newsletters'] = count_newsletters
        context_data['active_newsletters'] = active_newsletters
        return context_data


class ClientCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Создание клиента"""
    model = Client
    form_class = ClientForm
    success_url = reverse_lazy('news:index')
    permission_required = ('newsletter_app.add_client',)

    def form_valid(self, form):
        self.object = form.save()
        self.object.owner = self.request.user
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Редактирование клиента"""
    model = Client
    form_class = ClientForm
    permission_required = ('newsletter_app.change_client',)

    def get_success_url(self):
        return reverse_lazy('news:client', args=[self.object.pk])


class ClientDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Client
    permission_required = ('newsletter_app.view_client',)
    extra_context = {'title': 'Просмотр клиента'}


class ClientDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Удаление клиента"""
    model = Client
    success_url = reverse_lazy('news:index')
    permission_required = ('newsletter_app.delete_client',)

    def get_context_data(self, **kwargs):
        """
        Подтверждение удаления
        """
        context_data = super().get_context_data(**kwargs)
        client_item = Client.objects.get(pk=self.kwargs.get('pk'))
        context_data['client_pk'] = client_item.pk
        context_data['title'] = f'Удаление клиента {client_item}'
        return context_data


class NewsletterView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """Просмотр рассылок"""
    model = Newsletter
    permission_required = ('newsletter_app.view_newsletter',)
    extra_context = {'title': 'Рассылки'}

    def get_queryset(self):
        queryset = super().get_queryset()
        if (not self.request.user.is_staff and not self.request.user.is_superuser
                and not self.request.user.groups.filter(name='Moderators')):
            queryset = queryset.filter(owner=self.request.user).order_by('owner')
        return queryset.order_by('owner')


class NewsletterCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """создание рассылки"""
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
    """Редактирование рассылки"""
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
        """Склеивание форм рассылок и сообщений"""
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
    Переключение статуса рассылки для Модератора
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
    """Просмотр Логов"""
    model = Newsletter      # так проще:)
    extra_context = {'title': 'LoGs'}
    template_name = 'newsletter_app/logs_list.html'
    permission_required = 'newsletter_app.view_logs'

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(owner=self.request.user)
        return queryset
