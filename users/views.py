from django.shortcuts import render, redirect
from django.views.generic import CreateView, View
from users.models import User
from users.forms import UserRegisterForm
from django.urls import reverse_lazy, reverse
import random
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import PasswordResetView


# Create your views here.
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
        send_mail(
            subject='Верификация SkyStore',
            message=f'''Перейдите по ссылке для верификации: http://127.0.0.1:8000/users/verification_code/{code}
    и введите Логин и пароль''',
            from_email=settings.EMAIL_HOST_USER,
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
    except (ValueError, User.DoesNotExist):
        user = None
        messages.warning(request, 'Неверный код верификации')
    return redirect(reverse('users:login'))


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
            send_mail(
                subject='Восстановление пароля',
                message=f'Ваш новый пароль для авторизации: {new_password}',
                from_email=settings.EMAIL_HOST_USER,
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
