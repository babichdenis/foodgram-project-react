from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель для юзера."""

    email = models.EmailField(
        unique=True,
        max_length=254,
    )

    password = models.CharField(
        max_length=150,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    """Модель для подписок."""

    subscribing = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribing'
    )
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['subscriber', 'subscribing'],
                name='unique_name_subscribing'
            )
        ]

    def __str__(self):
        return f'{self.subscriber} подписан на {self.subscribing}'
