from django.conf.global_settings import EMAIL_HOST_USER
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone

from config.settings import CACHE_ENABLED
from newsletter.models import Mailing, Mailing_Attempt


def run_mailing(request, pk):
    """Функция запуска рассылки по требованию"""
    mailing = get_object_or_404(Mailing, id=pk)
    for recipient in mailing.recipients.all():
        try:
            mailing.status = "launched"
            send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email=EMAIL_HOST_USER,
                recipient_list=[recipient.email],
                fail_silently=False,
            )
            Mailing_Attempt.objects.create(
                attempt_date=timezone.now(),
                status="successful",
                server_response="Email отправлен",
                mailing=mailing,
            )
        except Exception as e:
            print(f"Ошибка при отправке письма для {recipient.email}: {str(e)}")
            Mailing_Attempt.objects.create(
                attempt_date=timezone.now(),
                status="unsuccessful",
                server_response=str(e),
                mailing=mailing,
            )
    if mailing.end_time and mailing.end_time <= timezone.now():
        # Если время рассылки закончилось, обновляем статус на "завершено"
        mailing.status = "completed"
    mailing.save()
    return redirect("newsletter:mailings")


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
