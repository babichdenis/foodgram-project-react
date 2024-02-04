from django.contrib.auth.models import AbstractUser
from django.db import models
from foodgram.constants import Constants


class FoodgramUser(AbstractUser):
    """
    Модель пользователя.
    Поле email переопределено для установки уникальности электронных
    почт пользователей.
    Дополнительное поле role - Выбор пользователь или администратор.
    """

    class Role(models.TextChoices):
        ADMIN = 'admin', 'admin'
        USER = 'user', 'user'

    email = models.EmailField(
        unique=True,
        verbose_name='Электронная почта'
    )
    role = models.CharField(
        choices=Role.choices,
        default=Role.USER,
        max_length=Constants.MAX_USERNAME_LENGTH,
        verbose_name='Роль'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def is_admin(self):
        return self.role == self.Role.ADMIN

    def __str__(self):
        return self.username


class Subscription(models.Model):
    '''Подписчики'''
    user = models.ForeignKey(
        FoodgramUser,
        related_name='follower',
        on_delete=models.CASCADE,
        verbose_name='Подписчик'
    )
    following = models.ForeignKey(
        FoodgramUser,
        verbose_name='Подписан',
        related_name='following',
        on_delete=models.CASCADE
    )
    added_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата подписки',
        editable=False
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'following'),
                name='user_followed_uniq'
            ),
            models.CheckConstraint(
                check=~models.Q(following=models.F('user')),
                name='user_is_not_following'
            ),
        )
        ordering = ('-added_date', )

    def __str__(self):
        return f'{self.user.username} -> {self.following.username}'
