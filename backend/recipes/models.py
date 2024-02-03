from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from foodgram.constants import Constants

User = get_user_model()


class Ingredient(models.Model):
    """
    Модель ингредиентов.
    Ограничения:
        - Ингредиенты и их ед. измерения не должны повторяться.
    """

    name = models.CharField(
        'Ингредиент',
        max_length=Constants.MAX_CHAR_LENGTH
    )
    measurement_unit = models.CharField(
        'Ед. измерения',
        max_length=Constants.MAX_CHAR_LENGTH
    )

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
        'Название тэга',
        max_length=Constants.MAX_CHAR_LENGTH,
        unique=True,
    )
    color = ColorField(
        'Цветовой HEX-код',
        max_length=Constants.MAX_COLOR_LENGTH,
        default="#FF0000",
    )
    slug = models.SlugField(
        'Slug',
        max_length=Constants.MAX_CHAR_LENGTH,
        unique=True,
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
    """
    Вспомогательная модель для связи рецептов и ингредиентов.
    Связи:
        - recipe -- Foreign Key c моделью Recipe.
        - ingredient -- Foreign Key c моделью Ingredient.
    Ограничения:
        - Количество ограничено минимальным и максимальным значением.
    """

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe_ingredient'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='ingredient_recipe'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                limit_value=Constants.MIN_AMOUNT,
                message='Минимальное значение "1".'),
            MaxValueValidator(
                limit_value=Constants.MAX_AMOUNT,
                message='Слишком большое значение.')],
        default=1,
        verbose_name='Количество'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='recipe_ingredient_uniq'
            ),
        )
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'

    def __str__(self):
        return f'{self.ingredient.name} -- {self.recipe.name}'


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
    recipe = models.ForeignKey(
        to=Recipe,
        verbose_name='Список покупок',
        related_name='shop_list',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        to=User,
        verbose_name='Пользователь',
        related_name='shop_list',
        on_delete=models.CASCADE
    )
    added_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления в список покупок',
        editable=False
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='shop_list__recipe_user_uniq'
            ),
        )
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'{self.recipe.name} -- {self.user.username}'
