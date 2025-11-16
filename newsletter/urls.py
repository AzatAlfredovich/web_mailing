from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from newsletter.apps import NewsletterConfig
from newsletter.views import (
    RecipientCreateView, RecipientDeleteView,
    RecipientDetailView, RecipientListView,
    RecipientUpdateView, MessageCreateView,
    MessageDeleteView, MessageDetailView,
    MessageListView, MessageUpdateView,
    MailingCreateView, MailingDeleteView,
    MailingDetailView, MailingUpdateView,
    MailingListView, HomeView)

app_name = NewsletterConfig.name

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("recipient/", RecipientListView.as_view(), name="recipients"),
    path("recipient/<int:pk>/", RecipientDetailView.as_view(), name="recipient_detail"),
   path("recipient/create/", RecipientCreateView.as_view(), name="recipient_create"),
    path(
        "recipient/<int:pk>/update/", RecipientUpdateView.as_view(), name="recipient_update"
    ),
    path(
        "recipient/<int:pk>/delete/", RecipientDeleteView.as_view(), name="recipient_delete"
    ),
    path("message/", MessageListView.as_view(), name="messages"),
    path("message/<int:pk>/", MessageDetailView.as_view(), name="message_detail"),
   path("message/create/", MessageCreateView.as_view(), name="message_create"),
    path(
        "message/<int:pk>/update/", MessageUpdateView.as_view(), name="message_update"
    ),
    path(
        "message/<int:pk>/delete/", MessageDeleteView.as_view(), name="message_delete"
    ),
path("mailing/", MailingListView.as_view(), name="mailings"),
    path("mailing/<int:pk>/", MailingDetailView.as_view(), name="mailing_detail"),
   path("mailing/create/", MailingCreateView.as_view(), name="mailing_create"),
    path(
        "mailing/<int:pk>/update/", MailingUpdateView.as_view(), name="mailing_update"
    ),
    path(
        "mailing/<int:pk>/delete/", MailingDeleteView.as_view(), name="mailing_delete"
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)