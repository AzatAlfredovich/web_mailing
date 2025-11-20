from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from newsletter.forms import (
    MailingForm,
    MailingModeratorForm, MessageForm, RecipientForm,
)
from newsletter.models import Mailing, Message, Recipient
from newsletter.services import get_mailing_from_cache


class HomeView(TemplateView):
    template_name = "newsletter/home.html"


# Дженерики класса Получатель
class RecipientListView(LoginRequiredMixin, ListView):
    model = Recipient

    def dispatch(self, request, *args, **kwargs):
        # Проверяем, имеет ли пользователь право на просмотр списка клиентов
        if not request.user.has_perm("newsletter.view_recipient"):
            return HttpResponseForbidden(
                "У вас нет прав для просмотра списка клиентов!"
            )
        return super().dispatch(request, *args, **kwargs)



class RecipientDetailView(DetailView):
    model = Recipient
    # newsletter/recipient_detail.html


class RecipientCreateView(CreateView):
    model = Recipient
    form_class = RecipientForm
    success_url = reverse_lazy("newsletter:recipients")
    # newsletter/recipient_form.html


class RecipientUpdateView(UpdateView):
    model = Recipient
    form_class = RecipientForm
    success_url = reverse_lazy("newsletter:recipients")
    # newsletter/recipient_form.html


class RecipientDeleteView(DeleteView):
    model = Recipient
    success_url = reverse_lazy("newsletter:recipients")
    # newsletter/recipient_confirm_delete.html


# Дженерики класса Сообщение
class MessageListView(ListView):
    model = Message


class MessageDetailView(DetailView):
    model = Message


class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("newsletter:messages")


class MessageUpdateView(UpdateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("newsletter:messages")


class MessageDeleteView(DeleteView):
    model = Message
    success_url = reverse_lazy("newsletter:messages")


# Дженерики класса Рассылка
class MailingListView(ListView):
    model = Mailing

    def dispatch(self, request, *args, **kwargs):
        # Проверяем, имеет ли пользователь право на просмотр списка клиентов
        if not request.user.has_perm("newsletter.view_mailing"):
            return HttpResponseForbidden(
                "У вас нет прав для просмотра списка рассылок!"
            )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return get_mailing_from_cache()


class MailingDetailView(DetailView):
    model = Mailing


class MailingCreateView(CreateView):
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy("newsletter:mailings")


class MailingUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy("newsletter:mailings")
    permission_required = "mailings.can_disable_mailing"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_active = not self.object.is_active
        self.object.save()
        return redirect(self.success_url)

    def handle_no_permission(self):
        return HttpResponseForbidden("У вас нет прав для отключения рассылки!")

    def get_form_class(self):
        user = self.request.user
        if user.is_superuser:
            return MailingForm
        if user.has_perm("newsletter.can_disable_mailing"):
            return MailingModeratorForm
        raise PermissionDenied


class MailingDeleteView(DeleteView):
    model = Mailing
    success_url = reverse_lazy("newsletter:mailings")
