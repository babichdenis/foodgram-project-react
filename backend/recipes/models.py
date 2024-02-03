from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from foodgram.constants import Constants

User = get_user_model()


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField('Ингредиент', max_length=Constants.MAX_CHAR_LENGTH)
    measurement_unit = models.CharField('Ед. измерения',
                                        max_length=Constants.MAX_CHAR_LENGTH)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient'),)

    def __str__(self):
        return f'{self.name}({self.measurement_unit})'


class Tag(models.Model):
    """ Модель тега. """

    name = models.CharField(
        max_length=Constants.MAX_CHAR_LENGTH,
        unique=True,
        verbose_name='Название тэга'
    )
    color = ColorField(
        "Цветовой HEX-код",
        max_length=Constants.MAX_COLOR_LENGTH,
        verbose_name='Цветовой код',
        default="#FF0000",
    )
    slug = models.SlugField(
        'Slug',
        max_length=Constants.MAX_CHAR_LENGTH,
        unique=True,
        verbose_name='Слаг'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""

    name = models.CharField(
        max_length=Constants.MAX_CHAR_LENGTH,
        verbose_name='Название'
    )
    text = models.TextField(verbose_name='Описание')
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Изображение'
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        verbose_name='Ингредиент',
        related_name='recipes',
        through='RecipeIngredient'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                limit_value=Constants.MIN_COOKING_TIME,
                message='Минимальное значение "1".'),
            MaxValueValidator(
                limit_value=Constants.MAX_COOKING_TIME,
                message='Слишком большое значение.')
        ],
        verbose_name='Время приготовления'
    )
    tags = models.ManyToManyField(
        'Tag',
        verbose_name='Тег',
        related_name='recipes',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='recipes',
        on_delete=models.CASCADE
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        editable=False
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'author'),
                name='recipe_name_author_uniq'
            ),
        )
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Связующая модель многие-ко-многим для ингредиентов и рецептов."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipeingredients')
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient')
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиента')

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient')]


class FavoritRecipe(models.Model):
    """Модель для избранных рецептов."""
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='favorites')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='favorites')

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite')]

    def __str__(self):
        return f'{self.user}, {self.recipe.name}'


class Cart(models.Model):
    """Модель для списка покупок."""
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='cart')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='cart')

    class Meta:
        verbose_name = "Рецепт в корзине"
        verbose_name_plural = "Рецепты в корзине"
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name="unique_recipe"
            )
        ]

    def __str__(self):
        return f'{self.user}, {self.recipe.name}'
