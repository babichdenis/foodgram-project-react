from django.contrib.auth.models import AbstractUser
from django.db import models


class FoodgramUser(AbstractUser):
    """
    Модель пользователя.
    """

    email = models.EmailField(
        unique=True,
        verbose_name='Электронная почта'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

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
