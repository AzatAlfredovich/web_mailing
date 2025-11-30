from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from users.models import CustomUser


class Command(BaseCommand):
    def handle(self, *args, **options):
        user = CustomUser.objects.create(email="admin@mail.ru")
        user.set_password("admin0000")
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
