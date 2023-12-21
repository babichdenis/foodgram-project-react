from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from backend.constants import MAX_EMAIL_LENGTH, MAX_USERNAME_LENGTH, REGEX


class CustomUser(AbstractUser):
    """Модель пользователя, расширяющая AbstractUser.
    с заменой username на email при авторизации.
    """

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']    

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
        unique=True,
        blank=False,
    )
    first_name = models.CharField(
        "Имя",
        unique=True,
        blank=False,
        max_length=MAX_USERNAME_LENGTH
        )
    last_name = models.CharField(
        "Фамилия",
        unique=True,
        blank=False,
        max_length=MAX_USERNAME_LENGTH
        )
    password = models.CharField(
        "Пароль",
        max_length=MAX_USERNAME_LENGTH,
        blank=False,
        validators=[
            RegexValidator(
                regex=REGEX,
                message="Недопустимый символ"),
        ],
    )

    class Meta:
        ordering = ("id",)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        """Возвращает строковое представление пользователя."""
        return self.username


class Subscribe(models.Model):
    """Модель для представления подписок пользователей."""

    user = models.ForeignKey(
        CustomUser,
        related_name='subscriber',
        verbose_name='Подписчик',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        CustomUser,
        related_name='author',
        verbose_name='Автор',
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ('author',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='users_cannot_rate_themselves'
            )
        ]

    def __str__(self):
        """Возвращает строковое представление подписки."""
        return f"{self.user.username} подписан(а) на {self.author.username}"
