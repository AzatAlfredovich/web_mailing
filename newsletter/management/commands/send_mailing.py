from django.conf.global_settings import EMAIL_HOST_USER
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone

from newsletter.models import Mailing, Mailing_Attempt


class Command(BaseCommand):
    help = "Отправляет выбранную рассылку вручную."

    def handle(self, *args, **kwargs):
        mailings = Mailing.objects.filter(status__in=["created", "started"])
        for mailing in mailings:
            for recipient in mailing.recipients.all():
                try:
                    send_mail(
                        mailing.message.subject,
                        mailing.message.body,
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
                    print(
                        f"Сообщение {mailing.message.subject} успешно отправлено на  {recipient.email}"
                    )
                except Exception as e:
                    Mailing_Attempt.objects.create(
                        attempt_date=timezone.now(),
                        status="unsuccessful",
                        server_response=str(e),
                        mailing=mailing,
                    )
                    print(str(e))
            mailing.save()
