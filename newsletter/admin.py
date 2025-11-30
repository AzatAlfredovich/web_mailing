from django.contrib import admin

from newsletter.models import Mailing, Mailing_Attempt, Message, Recipient


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "email",
        "comment",
    )
    list_filter = ("name",)
    search_fields = (
        "name",
        "email",
    )


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "subject",
        "body",
    )
    search_fields = ("subject",)


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = (
        "start_time",
        "end_time",
        "status",
    )
    search_fields = (
        "start_time",
        "end_time",
        "status",
    )


@admin.register(Mailing_Attempt)
class Mailing_AttemptAdmin(admin.ModelAdmin):
    list_display = (
        "attempt_date",
        "status",
        "mailing",
    )
    search_fields = (
        "attempt_date",
        "status",
    )
