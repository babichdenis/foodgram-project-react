from django.contrib.auth import get_user_model
from django.db import models
from foodgram.constants import MAX_CHAR_LENGTH, MAX_COLOR_LENGTH

User = get_user_model()


class Ingredient(models.Model):
    """Модель ингредиента."""
    name = models.CharField(
        "Ингредиент",
        max_length=MAX_CHAR_LENGTH,
    )
    measurement_unit = models.CharField(
        "Единица измерения",
        max_length=MAX_CHAR_LENGTH,
    )

    class Meta:
        verbose_name = "Ингридиент"
        verbose_name_plural = "Ингридиенты"
        ordering = ("name",)

    def __str__(self):
        return f'{self.name}({self.measurement_unit})'


class Tag(models.Model):
    ORANGE = '#FFA500'
    GREEN = '#008000'
    YELLOW = '#FFFF00'
    BLUE = '#0000FF'

    COLOR_CHOICES = [
        (ORANGE, 'Оранжевый'),
        (GREEN, 'Зеленый'),
        (YELLOW, 'Желтый'),
        (BLUE, 'Синий'),
    ]
    name = models.CharField(
        max_length=MAX_CHAR_LENGTH,
        unique=True,
        verbose_name='Название тэга'
    )
    color = models.CharField(
        max_length=MAX_COLOR_LENGTH,
        unique=True,
        choices=COLOR_CHOICES,
        default=BLUE,
        verbose_name='Цвет'
    )
    slug = models.SlugField(
        max_length=MAX_CHAR_LENGTH,
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
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes',
        verbose_name='Автор рецепта'
    )
    name = models.CharField(max_length=200, verbose_name='Название рецепта')
    image = models.ImageField(
        upload_to='recipes/', verbose_name='Изображение рецепта'
    )
    text = models.TextField(verbose_name='Описание рецепта')
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient', verbose_name='Ингредиенты'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления, мин.')
    tags = models.ManyToManyField(
        Tag, verbose_name='Тэги', related_name='recipes'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-id', )

    def __str__(self):
        return f'{self.author}, {self.name}'


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
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
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
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Владелец списка',
        related_name='shopping_cart',
        blank=False,
        null=False
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='in_shopping_cart',
        blank=False,
        null=False
    )

    class Meta:
        verbose_name = "Рецепт в корзине"
        verbose_name_plural = "Рецепты в корзине"
        ordering = ('user',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name="unique_recipe"
            )
        ]

    def __str__(self):
        return f'{self.user} добавил {self.recipe.name} в Список покупок'
