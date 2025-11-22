from datetime import timedelta

from django.conf.global_settings import EMAIL_HOST_USER
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone

from config import settings
from config.settings import CACHE_ENABLED
from newsletter.models import Mailing, Mailing_Attempt


def run_mailing(mailing: Mailing) -> None:
    """
    Отправка писем по рассылке и создание записей Mailing_Attempt.
    """

    recipients = mailing.recipients.all()
    if not recipients.exists():
        return

    subject = mailing.message.subject
    body = mailing.message.body
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@example.com")

    # Если рассылка только создана, то помечаем как запущенную
    if mailing.status == "created":
        mailing.status = "launched"
        mailing.save(update_fields=["status"])

    for recipient in recipients:
        try:
            sent_count = send_mail(
                subject,
                body,
                from_email,
                [recipient.email],
                fail_silently=False,
            )
            if sent_count:
                Mailing_Attempt.objects.create(
                    mailing=mailing,
                    status="successful",
                    server_response="Отправлено успешно",
                )
            else:
                Mailing_Attempt.objects.create(
                    mailing=mailing,
                    status="unsuccessful",
                    server_response="send_mail вернул 0 (письмо не отправлено)",
                )
        except Exception as e:
            Mailing_Attempt.objects.create(
                mailing=mailing, status="unsuccessful", server_response=str(e)
            )


@login_required
def block_mailing(request, pk):
    mailing = Mailing.objects.get(pk=pk)
    mailing.is_active = not mailing.is_active
    mailing.status = "completed"
    mailing.save()
    return redirect(reverse("newsletter:mailings"))


def get_mailing_from_cache():
    """Получение данных по рассылкам из кэша, если кэш пуст берем из БД."""
    if not CACHE_ENABLED:
        return Mailing.objects.all()
    key = "mailings"
    cache_data = cache.get(key)
    if cache_data is not None:
        return cache_data
    cache_data = Mailing.objects.all()
    cache.set(key, cache_data)
    return cache_data
