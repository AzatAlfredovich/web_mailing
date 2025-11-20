from django.contrib import admin

from users.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "email",
        "phone_number",
        "country",
    )
    list_filter = ("email",)
    search_fields = (
        "email",
        "country",
    )
