from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        'Создаёт группу "managers" (Менеджеры), назначает ей права, '
        'создаёт 1 пользователя с флагом is_manager=True и добавляет его в группу.'
    )

    def handle(self, *args, **options):
        group_name = "managers"
        CustomUser = get_user_model()

        # 1. Проверяем и создаём группу
        if Group.objects.filter(name=group_name).exists():
            self.stdout.write(self.style.WARNING(f'Группа "{group_name}" уже существует.'))
        else:
            group = Group.objects.create(name=group_name)
            self.stdout.write(self.style.SUCCESS(f'Группа "{group_name}" успешно создана.'))

        group = Group.objects.get(name=group_name)

        # 2. Назначаем права группе
        permissions_codenames = [
            'can_disable_mailing',
            'can_change_mailing',
            'can_view_mailing',
            'can_view_letter',
            'can_view_recipient',
            'can_block_user',
            'can_manage_users',
            'can_view_user',
        ]

        for codename in permissions_codenames:
            try:
                permission = Permission.objects.get(codename=codename)
                group.permissions.add(permission)
                self.stdout.write(self.style.SUCCESS(f'Право "{codename}" добавлено в группу.'))
            except Permission.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Право с codename="{codename}" не найдено в БД.')
                )

        # 3. Создаём пользователя
        email = 'manager@example.com'  # Основной идентификатор
        password = 'secure_password_123'  # Замените на безопасный пароль

        try:
            # Проверяем существование пользователя по email
            if CustomUser.objects.filter(email=email).exists():
                self.stdout.write(
                    self.style.WARNING(f'Пользователь с email="{email}" уже существует.')
                )
                return

            # Создаём пользователя
            user = CustomUser.objects.create(
                email=email,
                password=make_password(password),
                is_manager=True,  # Устанавливаем флаг
                # Остальные поля необязательны — можно добавить при необходимости
                # phone_number='+79991234567',
                # country='Россия',
            )

            user.groups.add(group)  # Добавляем в группу

            self.stdout.write(
                self.style.SUCCESS(
                    f'Пользователь (email="{email}") создан, добавлен в группу "{group_name}", '
                    'флаг is_manager=True установлен.'
                )
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка при создании пользователя: {e}'))

        self.stdout.write(self.style.SUCCESS('Настройка группы и пользователя завершена.'))
