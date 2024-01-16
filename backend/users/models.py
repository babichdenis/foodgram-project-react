from django.contrib.auth.models import AbstractUser
from django.db import models
from foodgram.constants import MAX_EMAIL_LENGTH, MAX_USERNAME_LENGTH


class User(AbstractUser):
    """Модель пользователя, расширяющая AbstractUser."""

    email = models.EmailField(
        'Электронная почта',
        max_length=MAX_EMAIL_LENGTH,
        unique=True
    )
    first_name = models.CharField(
        'Имя',
        max_length=MAX_USERNAME_LENGTH
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=MAX_USERNAME_LENGTH
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        """Возвращает строковое представление пользователя."""

        return self.username


class Subscription(models.Model):
    """Модель для представления подписок пользователей."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribe',
        verbose_name='Автор рецепта'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        unique_together = ('user', 'author')

        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='unique_subscribe'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='prevent_self_subscribe',
            )
        ]

    def __str__(self):
        return f'Пользователь {self.user} подписан на {self.author}'
