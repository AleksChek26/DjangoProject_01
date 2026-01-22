from django.conf import settings
from django.db import models
from django.utils import timezone


class Recipient(models.Model):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Получатель"
        verbose_name_plural = "Получатели"
        permissions = [
            ("can_manage_recipients", "Может управлять получателями"),
            ("view_recipient", "Может просматривать получателей"),
            ("add_recipient", "Может добавлять получателей"),
            ("change_recipient", "Может изменять получателей"),
            ("delete_recipient", "Может удалять получателей"),
        ]


class Message(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()

    def __str__(self):
        return self.subject

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        permissions = [
            ("can_manage_messages", "Может управлять сообщениями"),
            ("view_message", "Может просматривать сообщения"),
            ("add_message", "Может добавлять сообщения"),
            ("change_message", "Может изменять сообщения"),
            ("delete_message", "Может удалять сообщения"),
        ]


class Mailing(models.Model):
    STATUS_CHOICES = [
        ("Создана", "Создана"),
        ("Запущена", "Запущена"),
        ("Завершена", "Завершена"),
    ]

    start_time = models.DateTimeField(verbose_name="Начало рассылки")
    end_time = models.DateTimeField(verbose_name="Окончание рассылки")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="Создана", verbose_name="Статус"
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="mailings",
        verbose_name="Сообщение",
    )
    recipients = models.ManyToManyField(
        Recipient, related_name="mailings", verbose_name="Получатели"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mailings",
        verbose_name="Владелец",
    )  # владелец рассылки

    def update_status(self):
        now = timezone.now()
        if now < self.start_time:
            new_status = "Создана"
        elif self.start_time <= now <= self.end_time:
            new_status = "Запущена"
        else:
            new_status = "Завершена"

        if self.status != new_status:
            self.status = new_status
            self.save(update_fields=["status"])

    def __str__(self):
        return f"Рассылка: {self.message.subject}"

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        permissions = [
            ("can_manage_mailings", "Может управлять рассылками"),
            ("view_mailing", "Может просматривать рассылки"),
            ("add_mailing", "Может создавать рассылки"),
            ("change_mailing", "Может изменять рассылки"),
            ("delete_mailing", "Может удалять рассылки"),
            ("send_mailing", "Может отправлять рассылки"),  # доп. право
        ]


class Attempt(models.Model):
    STATUS_CHOICES = [
        ("Успешно", "Успешно"),
        ("Не успешно", "Не успешно"),
    ]

    attempt_time = models.DateTimeField(auto_now_add=True, verbose_name="Время попытки")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, verbose_name="Статус отправки"
    )
    server_response = models.TextField(
        blank=True, null=True, verbose_name="Ответ сервера"
    )
    mailing = models.ForeignKey(
        Mailing,
        on_delete=models.CASCADE,
        related_name="attempts",
        verbose_name="Рассылка",
    )

    def __str__(self):
        return f"Попытка {self.id} для рассылки {self.mailing.id}"

    class Meta:
        verbose_name = "Попытка отправки"
        verbose_name_plural = "Попытки отправки"
