from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group, Permission
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, View, ListView
from newsletter_app.models import Newsletter, Client, Message, Logs
from users.models import User
from users.forms import UserRegisterForm
from django.urls import reverse_lazy, reverse
import random
from django.conf import settings
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import PasswordResetView
from newsletter_app.services import mailing_util
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.contenttypes.models import ContentType


# Create your views here.
class UserListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """
    Контроллер просмотра пользователей
    """
    model = User
    permission_required = ('users.view_user',)
    extra_context = {'title': 'Список пользователей'}

    def get_context_data(self, *, object_list=None, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['object_list'] = User.objects.filter(is_superuser=False).order_by('email')
        # context_data['object_list'] = User.objects.order_by('email')
        return context_data


class UserRegView(CreateView):
    """
    Контроллер регистрации пользователя
    """
    model = User
    form_class = UserRegisterForm
    success_url = reverse_lazy('users:login')
    template_name = 'users/reg.html'

    def form_valid(self, form):
        """
        Верификация почты по ссылке
        """
        new_user = form.save()
        code = ''.join(random.sample(population='0123456789abcdefghijklmnopqrstuvwxyz', k=4))
        new_user.verification_code = code
        mailing_util(
            subject='Верификация SkyNews',
            message=f'''Перейдите по ссылке для верификации: http://127.0.0.1:8000/users/verification_code/{code}
    и введите Логин и пароль''',
            recipient_list=[new_user.email]
        )
        return super().form_valid(form)


def verify_mail(request, code):
    """
    Контроллер верификации email
    """
    try:
        user = User.objects.get(verification_code=code)
        user.is_active = True
        user.is_verified = True

        user.save()
        messages.success(request, 'Ваш аккаунт активирован!')

        users_group = Group.objects.filter(name='Users')
        print(users_group)
        if users_group:
            users_group = Group.objects.get(name='Users')
            user.groups.add(users_group)
        else:
            users_group = Group(name='Users')
            users_group.save()
            newsletter_content_type = ContentType.objects.get_for_model(Newsletter)
            add_permission = Permission.objects.get(codename="add_newsletter", content_type=newsletter_content_type)
            view_permission = Permission.objects.get(codename="view_newsletter", content_type=newsletter_content_type)
            change_permission = Permission.objects.get(codename="change_newsletter",
                                                       content_type=newsletter_content_type)
            delete_permission = Permission.objects.get(codename="delete_newsletter",
                                                       content_type=newsletter_content_type)
            users_group.permissions.add(add_permission, view_permission, change_permission, delete_permission)

            message_content_type = ContentType.objects.get_for_model(Message)
            add_permission = Permission.objects.get(codename="add_message", content_type=message_content_type)
            view_permission = Permission.objects.get(codename="view_message", content_type=message_content_type)
            change_permission = Permission.objects.get(codename="change_message", content_type=message_content_type)
            delete_permission = Permission.objects.get(codename="delete_message", content_type=message_content_type)
            users_group.permissions.add(add_permission, view_permission, change_permission, delete_permission)

            client_content_type = ContentType.objects.get_for_model(Client)
            add_permission = Permission.objects.get(codename="add_client", content_type=client_content_type)
            view_permission = Permission.objects.get(codename="view_client", content_type=client_content_type)
            change_permission = Permission.objects.get(codename="change_client", content_type=client_content_type)
            delete_permission = Permission.objects.get(codename="delete_client", content_type=client_content_type)
            users_group.permissions.add(add_permission, view_permission, change_permission, delete_permission)

            logs_content_type = ContentType.objects.get_for_model(Logs)
            add_permission = Permission.objects.get(codename="add_logs", content_type=logs_content_type)
            view_permission = Permission.objects.get(codename="view_logs", content_type=logs_content_type)
            change_permission = Permission.objects.get(codename="change_logs", content_type=logs_content_type)
            delete_permission = Permission.objects.get(codename="delete_logs", content_type=logs_content_type)
            users_group.permissions.add(add_permission, view_permission, change_permission, delete_permission)

            users_group.save()
            user.groups.add(users_group)
            user.save()
            # создаю группу модераторов с правами
            moderators_group, created = Group.objects.get_or_create(name='Moderators')
            if created:
                # Создаем группу сразу с разрешениями, если она только что была создана
                permissions = Permission.objects.filter(
                    codename__in=['set_is_active', 'set_status_send', 'view_newsletter']
                )
                moderators_group.permissions.set(permissions)
            moderators_group.save()

    except (ValueError, User.DoesNotExist):
        user = None
        messages.warning(request, 'Неверный код верификации')
    return redirect(reverse('users:login'))


def is_moderator(user):
    return user.groups.filter(name='Moderators').exists() or user.is_superuser


@login_required
@user_passes_test(test_func=is_moderator, login_url='users:login')
def toggle_activity(request, pk):
    """
    Функция переключения статуса is_active
    """
    user_item = get_object_or_404(User, pk=pk)
    if user_item.is_active:
        user_item.is_active = False
    else:
        user_item.is_active = True
    user_item.save()
    return redirect(reverse('newsletter_app:index'))


class UserForgotPassView(SuccessMessageMixin, PasswordResetView):
    """
    Контроллер сброса забытого пароля
    """
    form_class = PasswordResetForm
    from_email = settings.EMAIL_HOST_USER
    template_name = 'users/user_password_reset.html'
    success_url = reverse_lazy('users:login')
    success_message = 'Письмо с инструкцией по восстановлению пароля отправлено Вам на почту'
    email_template_name = 'users/mail_password_reset.html'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['title'] = 'Восстановление пароля'
        return context_data


class GenerateNewPasswordView(SuccessMessageMixin, View):
    """
    Контроллер генерирования нового пароля и отправки его на почту
    """

    def get(self, request, uidb64: str, token: str):
        user = self.get_user(uidb64)
        from django.contrib.auth.tokens import default_token_generator
        if not user or not default_token_generator.check_token(user, token):
            messages.warning(self.request, 'Ошибка идентификации пользователя, попробуйте ещё раз.')
        else:
            new_password = User.objects.make_random_password()
            user.set_password(new_password)
            user.save()
            mailing_util(
                subject='Восстановление пароля',
                message=f'Ваш новый пароль для авторизации: {new_password}',
                recipient_list=[user.email]
            )
            messages.success(request, 'Вам на почту отправлено письмо с новым паролем для вашего аккаунта')
        return redirect(reverse('users:login'))

    @staticmethod
    def get_user(uid_base64: str) -> User | None:
        try:
            from django.utils.http import urlsafe_base64_decode
            uid = urlsafe_base64_decode(uid_base64).decode()
            user_id = int(uid)
            user = User.objects.get(pk=user_id)
        except (ValueError, User.DoesNotExist):
            user = None
        return user
