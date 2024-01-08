from django.core.validators import RegexValidator
from django.db import models
from django.core import validators

from foodgram.constants import MAX_CHAR_LENGTH, MAX_COLOR_LENGTH, REGEX
from users.models import User


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
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ["id"]

    def __str__(self):
        """Возвращает строковое представление ингредиента."""
        return f"{self.name}({self.measurement_unit})"


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField("Название тэга", max_length=MAX_CHAR_LENGTH)
    color = models.CharField("Цветовой HEX-код", max_length=MAX_COLOR_LENGTH)
    slug = models.SlugField(
        "Slug",
        max_length=MAX_CHAR_LENGTH,
        unique=True,
        validators=[RegexValidator(
            regex=REGEX, message="Недопустимый символ")],
    )

    class Meta:
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"
        ordering = ["id"]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор рецепта",
    )
    name = models.CharField(
        "Название рецепта",
        max_length=MAX_CHAR_LENGTH,
    )
    image = models.ImageField(
        "Изображение рецепта",
        upload_to="recipes/",
    )
    text = models.TextField(verbose_name="Описание рецепта")
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        verbose_name="Ингредиенты",
    )
    cooking_time = models.PositiveSmallIntegerField(
        "Время приготовления, мин.",
        validators=[validators.MinValueValidator(
            1, message='Мин. время приготовления 1 минута'), ]
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Тэги",
        related_name="recipes"
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("-id",)

    def __str__(self):
        return f"{self.author}, {self.name}"


class RecipeIngredient(models.Model):
    """Связующая модель многие-ко-многим для ингредиентов и рецептов."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipeingredients",
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="ingredient",
        verbose_name="Ингредиент",
    )
    amount = models.PositiveSmallIntegerField(
        "Количество ингредиента",
        default=1,
        validators=(
            validators.MinValueValidator(
                1, message='Мин. количество ингридиентов 1'),),
    )

    class Meta:
        verbose_name = "Количество ингредиента"
        verbose_name_plural = "Количество ингредиентов"
        ordering = ["-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"],
                name="unique_ingredient",
            )
        ]

    def __str__(self):
        """Возвращает строковое представление ингредиента для рецепта."""
        return self.recipe.name


class FavoritRecipe(models.Model):
    """Модель для представления избранных рецептов."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name='Избранный рецепт'
    )

    class Meta:
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"
        ordering = ["-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_favorite")
        ]

    def __str__(self):
        """Возвращает строковое представление избранного рецепта."""
        list_ = [item['name'] for item in self.recipe.values('name')]
        return f'Пользователь {self.user} добавил {list_} в избранные. {self.user}, {self.recipe.name}'


class Cart(models.Model):
    """Модель для списка покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="cart",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="cart",
        verbose_name="Рецепт",
    )

    class Meta:
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"
        ordering = ["-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_recipe")
        ]

    def __str__(self):
        """Возвращает строковое представление списка покупок."""
        list_ = [item['name'] for item in self.recipe.values('name')]
        return f"Пользователь {self.user} добавил {list_} в покупки. {self.user}, {self.recipe.name}"
