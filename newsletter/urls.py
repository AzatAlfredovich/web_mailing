from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.views.decorators.cache import cache_page

from newsletter.apps import NewsletterConfig
from newsletter.views import (
    HomeView,
    MailingAttemptListView,
    MailingCreateView,
    MailingDeleteView,
    MailingDetailView,
    MailingListView,
    MailingUpdateView,
    MessageCreateView,
    MessageDeleteView,
    MessageDetailView,
    MessageListView,
    MessageUpdateView,
    RecipientCreateView,
    RecipientDeleteView,
    RecipientDetailView,
    RecipientListView,
    RecipientUpdateView,
)

app_name = NewsletterConfig.name

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("recipient/", cache_page(60)(RecipientListView.as_view()), name="recipients"),
    path(
        "recipient/<int:pk>/",
        cache_page(60)(RecipientDetailView.as_view()),
        name="recipient_detail",
    ),
    path("recipient/create/", RecipientCreateView.as_view(), name="recipient_create"),
    path(
        "recipient/<int:pk>/update/",
        RecipientUpdateView.as_view(),
        name="recipient_update",
    ),
    path(
        "recipient/<int:pk>/delete/",
        RecipientDeleteView.as_view(),
        name="recipient_delete",
    ),
    path("message/", cache_page(60)(MessageListView.as_view()), name="messages"),
    path(
        "message/<int:pk>/",
        cache_page(60)(MessageDetailView.as_view()),
        name="message_detail",
    ),
    path("message/create/", MessageCreateView.as_view(), name="message_create"),
    path(
        "message/<int:pk>/update/", MessageUpdateView.as_view(), name="message_update"
    ),
    path(
        "message/<int:pk>/delete/", MessageDeleteView.as_view(), name="message_delete"
    ),
    path("mailing/", cache_page(60)(MailingListView.as_view()), name="mailings"),
    path(
        "mailing/<int:pk>/",
        cache_page(60)(MailingDetailView.as_view()),
        name="mailing_detail",
    ),
    path("mailing/create/", MailingCreateView.as_view(), name="mailing_create"),
    path(
        "mailing/<int:pk>/update/", MailingUpdateView.as_view(), name="mailing_update"
    ),
    path(
        "mailing/<int:pk>/delete/", MailingDeleteView.as_view(), name="mailing_delete"
    ),
    path(
        "stats/", cache_page(60)(MailingAttemptListView.as_view()), name="attempt_list"
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
