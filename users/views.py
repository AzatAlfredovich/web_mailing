import secrets

from django.conf.global_settings import EMAIL_HOST_USER
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.db.models import Sum
from django.http import HttpResponseForbidden
from django.urls import reverse_lazy
from django.utils.crypto import get_random_string
from django.views.generic import ListView, TemplateView
from django.views.generic.edit import CreateView, FormView

from newsletter.models import Mailing
from users.forms import CustomUserCreationForm, PasswordRecoveryForm, CustomLoginForm
from users.models import CustomUser


class RegisterView(CreateView):
    template_name = "users/register.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("users:login")

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
        context_data["count_mailing"] = Mailing.objects.count()
        context_data["active_mailing_count"] = Mailing.objects.filter(
            status="launched"
        ).count()
        unique_clients_count = (
            Mailing.objects.values_list("recipients", flat=True).distinct().count()
        )
        context_data["unique_clients_count"] = unique_clients_count

        user = self.request.user
        user_mailings = Mailing.objects.filter(owner=user)
        context_data["total_successful_attempts"] = user_mailings.aggregate(
            Sum("successful_attempts")
        ).get("successful_attempts__sum", 0)
        context_data["total_unsuccessful_attempts"] = user_mailings.aggregate(
            Sum("unsuccessful_attempts")
        ).get("unsuccessful_attempts__sum", 0)
        context_data["total_sent_messages"] = user_mailings.aggregate(
            Sum("sent_messages")
        ).get("sent_messages__sum", 0)
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
        user = CustomUser.objects.get(email=email)
        length = 8
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        password = get_random_string(length, alphabet)
        user.set_password(password)
        user.save()
        send_mail(
            subject="Восстановление пароля",
            message=f"Ваш новый пароль: {password}",
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return super().form_valid(form)
