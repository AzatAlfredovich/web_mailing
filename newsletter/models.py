from django.db import models


class Recipient(models.Model):  # Получатель
    email = models.EmailField(
        unique=True,
        verbose_name="Почта",
        help_text="Введите почту",
    )
    name = models.CharField(
        max_length=100,
        verbose_name="Получатель",
        help_text="Введите получателя",
    )
    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name="Комментарий",
        help_text="Введите комментарий",
    )

    class Meta:
        verbose_name = "Получатель"
        verbose_name_plural = "Получатели"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Message(models.Model):  # Сообщение
    subject = models.CharField(
        max_length=50,
        verbose_name="Тема",
        help_text="Введите тему",
    )
    body = models.TextField(
        verbose_name="Тело письма",
        help_text="Введите текст письма",
    )

    class Meta:
        verbose_name = "Письмо"
        verbose_name_plural = "Письма"
        ordering = ["subject"]

    def __str__(self):
        return self.subject


class Mailing(models.Model):  # Рассылка
    # Список возможных статутов рассылки
    STATUS_CHOICES = [
        ("created", "Создана"),
        ("launched", "Запущена"),
        ("completed", "Завершена"),
    ]

    start_time = models.DateTimeField(
        verbose_name="Дата начала",
        blank=True,
        null=True,
    )
    end_time = models.DateTimeField(
        verbose_name="Дата окончания",
        blank=True,
        null=True,
    )
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="created", verbose_name="Статус"
    )
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, verbose_name="Сообщение"
    )
    recipients = models.ManyToManyField(
        Recipient, related_name="mailings", verbose_name="Получатели"
    )
    successful_attempts = models.IntegerField(default=0, verbose_name="Успешные попытки")
    unsuccessful_attempts = models.IntegerField(default=0, verbose_name="Неуспешные попытки")
    sent_messages = models.IntegerField(default=0, verbose_name="Сообщений отправлено")
    is_active = models.BooleanField(default=True, verbose_name="Рассылка активна")

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        ordering = ["status"]
        permissions = [
            ("can_disable_mailing", "Can disable mailing"),
        ]

    def __str__(self):
        return f"Рассылка {self.start_time} - {self.status}"


class Mailing_Attempt(models.Model):  # Попытка рассылки
    # Список возможных статутов попытки
    ATTEMPT_STATUSES = [("successful", "Успешно"), ("unsuccessful", "Не успешно")]

    attempt_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата попытки")
    status = models.CharField(
        max_length=15, choices=ATTEMPT_STATUSES, verbose_name="Статус"
    )
    server_response = models.TextField(
        null=True, blank=True, verbose_name="Ответ сервера"
    )
    mailing = models.ForeignKey(
        Mailing, on_delete=models.CASCADE, verbose_name="Рассылка"
    )

    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылки"
        ordering = ["status"]

    def __str__(self):
        return f"Попытка №{self.id}: {self.attempt_date}"
