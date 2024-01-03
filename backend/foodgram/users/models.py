from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class CustomUser(AbstractUser):

    """Модель для пользователя."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    username = models.CharField(
        max_length=150,
        unique=True,
        blank=False,
        validators=[
            RegexValidator(r'^[\w.@+-]+\Z'),
        ],
        verbose_name='Имя пользователя'
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        blank=False,
        verbose_name='Электронная почта'
    )
    first_name = models.CharField(
        max_length=150,
        unique=True,
        blank=False,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=150,
        unique=True,
        blank=False,
        verbose_name='Фамилия'
    )
    password = models.CharField(
        max_length=150,
        blank=False,
        validators=[
            RegexValidator(r'^[\w.@+-]+\Z'),
        ],
        verbose_name='Пароль'
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):

    """Модель для подписок."""

    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписики'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follow'
            )
        ]

    def __str__(self):
        return f'{self.user} {self.author}'
