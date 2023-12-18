from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
from backend.constants import (
    MAX_CHAR_LENGTH,
    MAX_COLOR_LENGTH,
    MIN_VAL,
    MAX_VAL,
    MAX_FIELD_LENGTH_RECIPE
)


User = get_user_model()


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField(
        "Название ингредиента",
        blank=False,
        max_length=MAX_CHAR_LENGTH
    )
    measurement_unit = models.CharField(
        "Единица измерения",
        max_length=MAX_CHAR_LENGTH
    )

    class Meta:
        ordering = ['name']
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        unique_together = ('name', 'measurement_unit')

    def __str__(self):
        return f"{self.name}, {self.measurement_unit}"


class Tag(models.Model):
    """Модель тегов"""

    name = models.CharField(
        "Название тэга",
        blank=False,
        unique=True,
        max_length=MAX_CHAR_LENGTH
        )
    color = models.CharField(
        "Цветовой HEX-код",
        unique=True,
        blank=False,
        default='#ffffff',
        max_length=MAX_COLOR_LENGTH
        )
    slug = models.SlugField(
        unique=True,
        blank=False,
        verbose_name='Слаг'
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        
        
class Recipe(models.Model):
    """Модель для представления рецептов."""

    tags = models.ManyToManyField(
        Tag,
        blank=False,
        related_name='recipes',
        verbose_name='Тэги'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        related_name='recipes',
    )
    text = models.TextField(
        null=True,
        default=None,
        verbose_name='Описание рецепта',
        max_length=MAX_FIELD_LENGTH_RECIPE
    )
    name = models.CharField(
        'Название рецепта',
        max_length=MAX_CHAR_LENGTH
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name="Изображение рецепта",
        blank=True,
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(
                MIN_VAL,
                f'Время приготовления не может быть меньше '
                f'{MIN_VAL} минуты'),
            MaxValueValidator(
                MAX_VAL,
                f'Время приготовления не может быть больше {MAX_VAL} минут')
        ]
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        related_name='recipes',
        verbose_name="Автор рецепта"
    )

    class Meta:
        ordering = ("-id",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return f"{self.author}, {self.name}."


class IngredientRecipe(models.Model):
    """Модель для представления ингредиентов в рецептах."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="ingredients",
        verbose_name="Ингредиент",
    )
    amount = models.IntegerField("Количество")

    class Meta:
        verbose_name = "Ингредиент для рецепта"
        verbose_name_plural = "Ингредиенты для рецепта"

    def __str__(self):
        """Возвращает строковое представление ингредиента для рецепта."""
        return self.recipe.name


class TagRecipe(models.Model):
    """Связанная модель рецепта и тега."""

    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тег'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    def __str__(self):
        return f'{self.recipe}: {self.tag}'


class Favorite(models.Model):
    """Модель избранного."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_follower',
        verbose_name="Рецепт",
    )

    class Meta:
        ordering = ("-id",)
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favourite')
        ]

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в Избранное'
