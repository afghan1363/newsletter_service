from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from users.views import UserRegView, UserForgotPassView, GenerateNewPasswordView, verify_mail, toggle_activity, UserListView

app_name = 'users'
urlpatterns = [
    path('', LoginView.as_view(template_name='users/login.html'), name='login'),
    path('users_list/', UserListView.as_view(), name='users_list'),
    path('registration/', UserRegView.as_view(), name='reg'),
    path('verification_code/<str:code>', verify_mail, name='verification_code'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('forgot_pass/', UserForgotPassView.as_view(), name='forgot_pass'),
    path('set_new_password/<uidb64>/<token>/', GenerateNewPasswordView.as_view(), name='set_new_password'),
    path('activity/<int:pk>', toggle_activity, name='toggle_activity')
]
