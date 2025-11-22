from django.forms import ModelForm

from newsletter.models import Mailing, Message, Recipient


class MailingForm(ModelForm):
    class Meta:
        model = Mailing
        exclude = ("owner",)

    def __init__(self, *args, **kwargs):
        super(MailingForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.help_text = ""

        self.fields["start_time"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Начало отправки YYYY-MM-DD HH:MM"}
        )

        self.fields["end_time"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Окончание отправки YYYY-MM-DD HH:MM",
            }
        )

        self.fields["status"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Статус рассылки"}
        )

        self.fields["message"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Сообщение"}
        )

        self.fields["recipients"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Получатели"}
        )
        self.fields["successful_attempts"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Успешные попытки"}
        )

        self.fields["unsuccessful_attempts"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Неуспешные попытки"}
        )

        self.fields["sent_messages"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Сообщений отправлено"}
        )

        self.fields["is_active"].widget.attrs.update({"class": "form-check-input"})


class RecipientForm(ModelForm):
    class Meta:
        model = Recipient
        exclude = ("owner",)

    def __init__(self, *args, **kwargs):
        super(RecipientForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.help_text = ""

        self.fields["email"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Почта"}
        )

        self.fields["name"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Имя или никнейм"}
        )

        self.fields["comment"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Комментарий"}
        )


class MessageForm(ModelForm):
    class Meta:
        model = Message
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.help_text = ""

        self.fields["subject"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Заголовок"}
        )

        self.fields["body"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Содержание"}
        )


class MailingModeratorForm(ModelForm):
    class Meta:
        model = Mailing
        fields = ("is_active",)

    def __init__(self, *args, **kwargs):
        super(MailingModeratorForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.help_text = ""
        self.fields["is_active"].widget.attrs.update({"class": "form-check-input"})
