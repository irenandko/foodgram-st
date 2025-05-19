from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from foodgram.constants import (USER_NAMES_MAX_LENGTH,
                                USER_EMAIL_MAX_LENGTH,
                                USER_NICKNAME_MAX_LENGTH,
                                USER_REGEX_CONTROLLER)


class CustomUser(AbstractUser):
    """Класс пользователя."""

    REQUIRED_FIELDS = ["username", "first_name", "last_name"]  # for superuser
    USERNAME_FIELD = "email"                                   # login

    first_name = models.CharField(
        max_length=USER_NAMES_MAX_LENGTH,
        verbose_name="Имя")
    last_name = models.CharField(
        max_length=USER_NAMES_MAX_LENGTH,
        verbose_name="Фамилия",
    )
    email = models.EmailField(
        max_length=USER_EMAIL_MAX_LENGTH,
        unique=True,
        verbose_name="Электронная почта"
    )
    username = models.CharField(
        max_length=USER_NICKNAME_MAX_LENGTH,
        unique=True,
        validators=[
            RegexValidator(
                regex=USER_REGEX_CONTROLLER,
                message="Некорректное имя пользователя")],
        verbose_name="Имя пользователя",
    )
    avatar = models.ImageField(
        upload_to="avatars/",
        null=True,
        blank=True,
        verbose_name="Фото профиля"
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("username",)

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Класс отображения подписки."""

    user: models.ForeignKey = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    author: models.ForeignKey = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscribers'
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_subscription'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан(-а) на {self.author}'
