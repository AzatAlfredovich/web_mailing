import secrets

from django.conf.global_settings import EMAIL_HOST_USER
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.db.models import Sum
from django.http import HttpResponseForbidden
from django.urls import reverse_lazy
from django.utils.crypto import get_random_string
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import CreateView, FormView, UpdateView

from newsletter.models import Mailing
from users.forms import (CustomLoginForm, CustomUserCreationForm,
                         PasswordRecoveryForm, UserProfileForm)
from users.models import CustomUser


class RegisterView(CreateView):
    template_name = "users/register.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("users:email_confirmation")

    def form_valid(self, form):
        user = form.save()
        user.is_active = False
        token = secrets.token_hex(16)
        host = self.request.get_host()
        url = f"http://{host}/users/email_confirm/{token}/"
        user.token = token
        user.save()
        send_mail(
            subject="Подтверждение почты",
            message=f"Здравствуйте, перейдите по ссылке для подтверждения почты: {url} ",
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email],
        )
        return super().form_valid(form)


class CustomLoginView(LoginView):
    template_name = "users/login.html"
    authentication_form = CustomLoginForm


class UsersListView(LoginRequiredMixin, ListView):
    model = CustomUser
    template_name = "users/users_list.html"

    def dispatch(self, request, *args, **kwargs):
        # Проверяем, имеет ли пользователь право на просмотр списка клиентов
        if not request.user.has_perm("users.view_customuser"):
            return HttpResponseForbidden(
                "У вас нет прав для просмотра списка пользователей!"
            )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        user = self.request.user
        user_mailings = Mailing.objects.filter(owner=user)
        context_data["total_successful_attempts"] = (
            user_mailings.aggregate(Sum("successful_attempts"))[
                "successful_attempts__sum"
            ]
            or 0
        )
        context_data["total_unsuccessful_attempts"] = (
            user_mailings.aggregate(Sum("unsuccessful_attempts"))[
                "unsuccessful_attempts__sum"
            ]
            or 0
        )
        context_data["total_sent_messages"] = (
            user_mailings.aggregate(Sum("sent_messages"))["sent_messages__sum"] or 0
        )
        return context_data


class EmailConfirmationView(TemplateView):
    model = CustomUser
    template_name = "users/email_confirmation.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Письмо активации отправлено!"
        return context


class PasswordRecoveryView(FormView):
    template_name = "users/password_recovery.html"
    form_class = PasswordRecoveryForm
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        email = form.cleaned_data["email"]

        # 1. Проверка существования пользователя
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            form.add_error("email", "Пользователь с таким email не найден.")
            return self.form_invalid(form)

        # 2. Корректная генерация пароля (исправлена опечатка в алфавите)
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        password = get_random_string(length=8, allowed_chars=alphabet)

        # 3. Сохранение нового пароля
        user.set_password(password)
        user.save()

        # 4. Отправка письма с обработкой ошибок
        try:
            send_mail(
                subject="Восстановление пароля",
                message=f"Ваш новый пароль: {password}\n\nСмените его в настройках профиля.",
                from_email=EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception as e:
            form.add_error(None, "Не удалось отправить письмо. Попробуйте позже.")
            return self.form_invalid(form)

        return super().form_valid(form)


class UserProfileDetailView(LoginRequiredMixin, DetailView):
    """
    Представление для отображения детальной информации о профиле пользователя.
    Доступ только для авторизованных пользователей.
    """

    model = CustomUser
    template_name = "users/profile_detail.html"
    context_object_name = "user"

    def get_object(self, queryset=None):
        """
        Возвращает текущего пользователя (профиль которого просматривается).
        Переопределяем, чтобы показывать только собственный профиль.
        """
        return self.request.user

    def get_context_data(self, **kwargs):
        """
        Добавляет дополнительные данные в контекст шаблона.
        """
        context = super().get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        """
        Переопределяем GET-запрос для дополнительной логики.
        """
        # Вызываем родительский метод для стандартной обработки
        return super().get(request, *args, **kwargs)


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = UserProfileForm
    template_name = "users/profile_form.html"
    success_url = reverse_lazy("users:profile_detail")

    def get_object(self, queryset=None):
        """Возвращаем текущего пользователя"""
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Форма уже будет в контексте как 'form'
        return context
