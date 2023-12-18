from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

from backend.constants import MAX_EMAIL_LENGTH, MAX_USERNAME_LENGTH, REGEX


class CustomUser(AbstractUser):
    """Модель пользователя, расширяющая AbstractUser.
    с заменой username на email при авторизации.
    """

    username = models.CharField(
        "Логин",
        max_length=MAX_USERNAME_LENGTH,
        unique=True,
        validators=[
            RegexValidator(
                regex=REGEX,
                message="Недопустимый символ"
                )
        ],
    )
    email = models.EmailField(
        "email address",
        max_length=MAX_EMAIL_LENGTH,
        unique=True
    )
    first_name = models.CharField(
        "Имя",
        max_length=MAX_USERNAME_LENGTH
        )
    last_name = models.CharField(
        "Фамилия",
        max_length=MAX_USERNAME_LENGTH
        )
    password = models.CharField(
        "Пароль",
        max_length=MAX_USERNAME_LENGTH,
        validators=[
            RegexValidator(
                regex=REGEX,
                message="Недопустимый символ"),
        ],
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ("id",)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        """Возвращает строковое представление пользователя."""
        return self.username
