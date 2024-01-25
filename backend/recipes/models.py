from colorfield.fields import ColorField
from django.core import validators
from django.core.validators import RegexValidator
from django.db import models
from foodgram.constants import (MAX_CHAR_LENGTH, MAX_COLOR_LENGTH, REGEX)
from django.db.models import (
    CheckConstraint,
    UniqueConstraint,
    DateTimeField,
    Q,
)
from recipes.validators import hex_color_validator
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
        verbose_name = "Ингридиент"
        verbose_name_plural = "Ингридиенты"
        ordering = ("name",)

    def __str__(self):
        return f"{self.name}({self.measurement_unit})"

    def clean(self):
        self.name = self.name.lower()
        self.measurement_unit = self.measurement_unit.lower()
        super().clean()


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(
        "Название тэга",
        max_length=MAX_CHAR_LENGTH
    )
    color = ColorField(
        "Цветовой HEX-код",
        max_length=MAX_COLOR_LENGTH,
        default="#FF0000",
    )
    slug = models.SlugField(
        "Slug",
        max_length=MAX_CHAR_LENGTH,
        unique=True,
        validators=[
            RegexValidator(
                regex=REGEX,
                message="Недопустимый символ"
            )
        ],
    )

    class Meta:
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"
        ordering = ("name",)

    def __str__(self) -> str:
        return f"{self.name} (цвет: {self.color})"

    def clean(self) -> None:
        self.name = self.name.strip().lower()
        self.slug = self.slug.strip().lower()
        self.color = hex_color_validator(self.color)
        return super().clean()


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
        validators=[
            validators.MinValueValidator(
                1,
                message="Мин. время приготовления 1 минута"
            ),
        ],
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Тэги",
        related_name="recipes"
    )
    pub_date = DateTimeField(
        verbose_name="Дата публикации",
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("-pub_date",)

    def __str__(self):
        return f"{self.name}. Автор: {self.author.username}"

    def clean(self):
        self.name = self.name.capitalize()
        return super().clean()


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
                1,
                message="Мин. количество ингридиентов 1",
            ),
        ),
    )

    class Meta:
        verbose_name = "Количество ингредиента"
        verbose_name_plural = "Количество ингредиентов"
        ordering = ("recipe",)

    def __str__(self):
        return f"{self.recipe} {self.ingredient}"


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
        verbose_name="Избранный рецепт",
    )
    date_added = DateTimeField(
        verbose_name="Дата добавления", auto_now_add=True, editable=False
    )

    class Meta:
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"
        ordering = ["-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_favorite"
            )
        ]

    def __str__(self):
        return f"Пользователь {self.user} добавил \
            {self.recipe.name} в избранное."


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
    date_added = DateTimeField(
        verbose_name="Дата добавления", auto_now_add=True, editable=False
    )

    class Meta:
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"
        ordering = ["-id"]

    def __str__(self):
        return f"Пользователь {self.user} добавил \
            {self.recipe.name} в покупки."
