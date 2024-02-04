from django.contrib.auth.models import AbstractUser
from django.db import models
from foodgram.constants import Constants


class User(AbstractUser):
    '''Пользователь (В рецепте - автор рецепта)'''

    email = models.EmailField(
        max_length=Constants.MAX_EMAIL_LENGTH,
        unique=True,
        verbose_name='Адрес электронной почты'
    )
    first_name = models.CharField(
        max_length=Constants.MAX_USERNAME_LENGTH,
        blank=True,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=Constants.MAX_USERNAME_LENGTH,
        blank=True,
        verbose_name='Фамилия'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username


class Subscription(models.Model):
    '''Подписчики'''
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
        verbose_name='Подписчик'
    )
    following = models.ForeignKey(
        User,
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
