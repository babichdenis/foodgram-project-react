from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator, RegexValidator

from users.models import CustomUser


User = get_user_model()


class Ingredient(models.Model):

    """Модель Ингридиента."""

    name = models.CharField(
        max_length=255,
        verbose_name='Название Ингридиента'
    )
    measurement_unit = models.CharField(
        max_length=50,
        verbose_name='Еденицы измерения'
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Tag(models.Model):

    """Модель Тега."""

    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название Тега'
    )
    color = ColorField(
        max_length=7,
        format='hex',
        unique=True,
        verbose_name='Цвет Тега',
        validators=[
            RegexValidator(
                regex="^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
                message='Проверьте вводимый формат',
            )
        ],
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='Слаг Тега'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'color', 'slug'),
                name='unique_tags',
            ),
        )

    def __str__(self):
        return self.name


class Recipe(models.Model):

    """Модель рецепта."""

    author = models.ForeignKey(
        CustomUser,
        related_name='recipes',
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта'
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Фото рецепта',
        help_text='Добавьте фото'
    )
    text = models.TextField(
        verbose_name='Текстовое описание',
        help_text='Введите описание рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientAmount',
        related_name='recipes',
        verbose_name='Ингридиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                1, message='Минимальное значение для поля - 1!!!'
            )
        ],
        verbose_name='Время приготовления'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-id']

    def __str__(self):
        return self.name


class IngredientAmount(models.Model):

    """Связная модель для Ингридиентов и Рецпетов."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingridient_list',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingridient_list',
        verbose_name='Ингридиент'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Количество Ингридиента'
        verbose_name_plural = 'Количество Ингридиентов'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_ingredient_amount'
            )
        ]

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'


class FavoriteRecipe(models.Model):

    """Модель для Избранного рецепта."""

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Избранный рецепт'
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_recipe'
            )
        ]

    def __str__(self):
        return f'{self.user} {self.recipe}'


class ShoppingCart(models.Model):

    """Модель корзины покупок."""

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='shopping_user',
        verbose_name='Покупатель'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_recipe',
        verbose_name='Покупка'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            )
        ]

    def __str__(self):
        return f'{self.user} {self.recipe}'
