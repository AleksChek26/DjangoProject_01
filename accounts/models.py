from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Расширенная модель пользователя."""
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('Телефон')
    )
    birth_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Дата рождения')
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name=_('Аватар')
    )
    country = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Страна')
    )

    # Переопределяем поле email, чтобы сделать его обязательным и уникальным
    email = models.EmailField(
        _('email address'),
        unique=True,
        help_text=_('Обязательное поле. Укажите корректный email.'),
    )

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')
