from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  TemplateView, UpdateView)

from newsletter.models import Recipient, Message, Mailing, Mailing_Attempt


class HomeView(TemplateView):
    template_name = "newsletter/home.html"

# Дженерики класса Получатель
class RecipientListView(ListView):
    model = Recipient
    # newsletter/recipient_list.html


class RecipientDetailView(DetailView):
    model = Recipient
    # newsletter/recipient_detail.html


class RecipientCreateView(CreateView):
    model = Recipient
    fields = ("email", "name", "comment")
    success_url = reverse_lazy("newsletter:recipients")
    # newsletter/recipient_form.html


class RecipientUpdateView(UpdateView):
    model = Recipient
    fields = ("email", "name", "comment")
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
    fields = ("subject", "body")
    success_url = reverse_lazy("newsletter:messages")


class MessageUpdateView(UpdateView):
    model = Message
    fields = ("subject", "body")
    success_url = reverse_lazy("newsletter:messages")


class MessageDeleteView(DeleteView):
    model = Message
    success_url = reverse_lazy("newsletter:messages")


# Дженерики класса Рассылка
class MailingListView(ListView):
    model = Mailing


class MailingDetailView(DetailView):
    model = Mailing


class MailingCreateView(CreateView):
    model = Mailing
    fields = ("start_time", "end_time", "status", "message", "recipients")
    success_url = reverse_lazy("newsletter:mailings")


class MailingUpdateView(UpdateView):
    model = Mailing
    fields = ("start_time", "end_time", "status", "message", "recipients")
    success_url = reverse_lazy("newsletter:mailings")


class MailingDeleteView(DeleteView):
    model = Mailing
    success_url = reverse_lazy("newsletter:mailings")


