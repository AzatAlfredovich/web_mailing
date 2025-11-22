from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  TemplateView, UpdateView)

from newsletter.forms import (MailingForm, MailingModeratorForm, MessageForm,
                              RecipientForm)
from newsletter.models import Mailing, Mailing_Attempt, Message, Recipient
from newsletter.services import get_mailing_from_cache


class RoleBasedMixin:
    """
    Определяет роли пользователя:
    - is_manager: явный менеджер (is_manager=True)
    - is_superuser: суперпользователь (is_superuser=True)
    - has_user_management: право управлять пользователями (или суперпользователь)
    """

    def dispatch(self, request, *args, **kwargs):
        self.is_manager = request.user.is_manager
        self.is_superuser = request.user.is_superuser
        self.has_user_management = (
            request.user.has_perm("users.can_manage_users") or self.is_superuser
        )
        return super().dispatch(request, *args, **kwargs)

    def get_owner_filter(self):
        """
        Возвращает фильтр для запросов:
        - Суперпользователь/менеджер: все объекты ({}).
        - Обычный пользователь: только свои (owner=request.user).
        """
        if self.is_superuser or self.is_manager:
            return {}
        return {"owner": self.request.user}


class HomeView(TemplateView):
    template_name = "newsletter/home.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["count_mailing"] = Mailing.objects.count()
        context_data["active_mailing_count"] = Mailing.objects.filter(
            status="launched"
        ).count()
        unique_clients_count = Mailing.objects.values("recipients").distinct().count()
        context_data["unique_clients_count"] = unique_clients_count
        return context_data


# Дженерики класса Получатель
class RecipientListView(RoleBasedMixin, LoginRequiredMixin, ListView):
    model = Recipient

    def get_queryset(self):
        return Recipient.objects.filter(**self.get_owner_filter())

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        if not request.user.has_perm("newsletter.view_recipient"):
            return redirect("users:login")
        return super().dispatch(request, *args, **kwargs)


class RecipientDetailView(RoleBasedMixin, LoginRequiredMixin, DetailView):
    model = Recipient

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if (
            not self.is_manager
            and obj.owner != self.request.user
            and not self.is_superuser
        ):
            raise PermissionDenied("У вас нет доступа к этому получателю")
        return obj

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        if not request.user.has_perm("newsletter.view_recipient"):
            raise PermissionDenied("У вас нет прав на просмотр получателя")
        return super().dispatch(request, *args, **kwargs)


class RecipientCreateView(RoleBasedMixin, LoginRequiredMixin, CreateView):
    model = Recipient
    form_class = RecipientForm
    success_url = reverse_lazy("newsletter:recipients")

    def form_valid(self, form):
        if not self.is_manager:
            form.instance.owner = self.request.user
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        if not request.user.has_perm("newsletter.add_recipient"):
            raise PermissionDenied("У вас нет прав на создание получателя")
        return super().dispatch(request, *args, **kwargs)


class RecipientUpdateView(RoleBasedMixin, LoginRequiredMixin, UpdateView):
    model = Recipient
    form_class = RecipientForm
    success_url = reverse_lazy("newsletter:recipients")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if (
            not self.is_manager
            and obj.owner != self.request.user
            and not self.is_superuser
        ):
            raise PermissionDenied("Вы не можете редактировать этого получателя")
        return obj

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        if not request.user.has_perm("newsletter.change_recipient"):
            raise PermissionDenied("У вас нет прав на редактирование получателя")
        return super().dispatch(request, *args, **kwargs)


class RecipientDeleteView(RoleBasedMixin, LoginRequiredMixin, DeleteView):
    model = Recipient
    success_url = reverse_lazy("newsletter:recipients")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if (
            not self.is_manager
            and obj.owner != self.request.user
            and not self.is_superuser
        ):
            raise PermissionDenied("Вы не можете удалить этого получателя")
        return obj

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        if not request.user.has_perm("newsletter.delete_recipient"):
            raise PermissionDenied("У вас нет прав на удаление получателя")
        return super().dispatch(request, *args, **kwargs)


# Дженерики класса Сообщение
class MessageListView(LoginRequiredMixin, ListView):
    model = Message


class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("newsletter:messages")


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("newsletter:messages")


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    success_url = reverse_lazy("newsletter:messages")


# Дженерики класса Рассылка
class MailingListView(RoleBasedMixin, LoginRequiredMixin, ListView):
    model = Mailing

    def get_queryset(self):
        base_queryset = get_mailing_from_cache()
        return base_queryset.filter(**self.get_owner_filter()).select_related("message")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        if not request.user.has_perm("newsletter.view_mailing"):
            return redirect("users:login")
        return super().dispatch(request, *args, **kwargs)


class MailingDetailView(RoleBasedMixin, LoginRequiredMixin, DetailView):
    model = Mailing

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if (
            not self.is_manager
            and obj.owner != self.request.user
            and not self.is_superuser
        ):
            raise PermissionDenied("У вас нет доступа к этой рассылке")
        return obj

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        if not request.user.has_perm("newsletter.view_mailing"):
            raise PermissionDenied("У вас нет прав на просмотр рассылки")
        return super().dispatch(request, *args, **kwargs)


class MailingCreateView(RoleBasedMixin, LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy("newsletter:mailings")

    def form_valid(self, form):
        if not self.is_manager:
            form.instance.owner = self.request.user
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        if not request.user.has_perm("newsletter.add_mailing"):
            return redirect("users:login")
        return super().dispatch(request, *args, **kwargs)


class MailingUpdateView(RoleBasedMixin, LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy("newsletter:mailings")

    def get_form_class(self):
        user = self.request.user
        if user.is_superuser:
            return MailingForm  # Полная форма для суперпользователя
        if self.is_manager:
            return MailingModeratorForm  # Ограниченная форма для менеджеров
        if user.has_perm("newsletter.change_mailing"):
            return MailingForm
        raise PermissionDenied("У вас недостаточно прав")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if (
            not self.is_manager
            and obj.owner != self.request.user
            and not self.is_superuser
        ):
            raise PermissionDenied("Вы не можете редактировать эту рассылку")
        return obj

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        if not request.user.has_perm("newsletter.change_mailing"):
            raise PermissionDenied("У вас нет прав на редактирование рассылки")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        mailing = form.save(commit=False)

        # Логика статусов
        if mailing.is_active:
            # Если активна — сохраняем выбранный статус (из допустимых)
            # Форма уже проверит choices благодаря __init__
            pass
        else:
            # Если неактивна — принудительно ставим "completed"
            mailing.status = "completed"

        mailing.save()
        return super().form_valid(form)


class MailingDeleteView(RoleBasedMixin, LoginRequiredMixin, DeleteView):
    model = Mailing
    success_url = reverse_lazy("newsletter:mailings")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if (
            not self.is_manager
            and obj.owner != self.request.user
            and not self.is_superuser
        ):
            raise PermissionDenied("Вы не можете удалить эту рассылку")
        return obj

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        if not request.user.has_perm("newsletter.delete_mailing"):
            raise PermissionDenied("У вас нет прав на удаление рассылки")
        return super().dispatch(request, *args, **kwargs)


class MailingAttemptListView(RoleBasedMixin, LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "newsletter/attempt_list.html"
    context_object_name = "object_list"

    def get_queryset(self):
        # Оптимизируем запросы: сразу подтягиваем попытки
        if self.is_superuser:
            return Mailing.objects.prefetch_related("mailing_attempt_set")
        return Mailing.objects.filter(owner=self.request.user).prefetch_related(
            "mailing_attempt_set"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        for mailing in context["object_list"]:
            # Получаем все попытки для рассылки
            attempts = mailing.mailing_attempt_set.all()

            # Считаем статусы
            successful = sum(1 for a in attempts if a.status == "successful")
            unsuccessful = sum(1 for a in attempts if a.status == "unsuccessful")
            total = successful + unsuccessful

            # Обновляем атрибуты объекта (для шаблона)
            mailing.successful_attempts = successful
            mailing.unsuccessful_attempts = unsuccessful
            mailing.sent_messages = 0  # Не можем посчитать без sent_count

            # Рассчитываем процент успешности
            if total > 0:
                mailing.success_rate = round((successful / total) * 100, 1)
            else:
                mailing.success_rate = 0.0

        return context
