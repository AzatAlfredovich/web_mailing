from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.forms import BooleanField, ImageField

from users.models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        max_length=30,
        required=True,
        help_text="Поле обязательно к заполнению. Введите почту.",
    )
    avatar = forms.ImageField(
        required=False,
        help_text="Поле необязательно к заполнению. Загрузите изображение.",
    )
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        help_text="Поле необязательно к заполнению. Введите номер телефона.",
    )
    country = forms.CharField(
        max_length=30,
        required=False,
        help_text="Поле необязательно к заполнению. Введите страну проживания.",
    )
    usable_password = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].label = "Почта"
        self.fields["phone_number"].label = "Номер телефона"
        self.fields["country"].label = "Страна проживания"
        self.fields["avatar"].label = "Фотография профиля"
        self.fields["password1"].label = "Пароль"
        self.fields["password2"].label = "Повторите пароль"
        for field_name, field in self.fields.items():
            field.help_text = ""
            if isinstance(field, BooleanField):
                field.widget.attrs["class"] = "form-check-input"
            elif isinstance(field, ImageField):
                field.widget.attrs["class"] = "form-control-file"
            else:
                field.widget.attrs["class"] = "form-control"

    class Meta:
        model = CustomUser
        fields = (
            "email",
            "phone_number",
            "country",
            "avatar",
            "password1",
            "password2",
        )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с такой почтой уже зарегистрирован!")
        else:
            return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if phone_number and not phone_number.isdigit():
            raise forms.ValidationError(
                "Номер телефона должен состоять только из цифр!"
            )
        return phone_number


class PasswordRecoveryForm(forms.Form):
    email = forms.EmailField(label="Укажите Email")

    def clean_email(self):
        """
        Проверка email на уникальность
        """
        email = self.cleaned_data.get("email")
        if not CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Такого email нет в системе")
        return email


class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Настраиваем лейблы полей
        self.fields["username"].label = "Почта"
        self.fields["password"].label = "Пароль"

        # Оформляем поля формы с помощью Bootstrap-классов
        self.fields["username"].widget.attrs.update(
            {
                "class": "form-control",
            }
        )
        self.fields["password"].widget.attrs.update(
            {
                "class": "form-control",
            }
        )
