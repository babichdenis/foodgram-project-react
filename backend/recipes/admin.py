from django.contrib import admin

from users.models import Subscription
from recipes.models import (
    Cart,
    FavoritRecipe,
    Ingredient,
    Recipe,
    RecipeIngredient,
    Tag,
)


class RecipeIngredientInLine(admin.TabularInline):
    """Inline для отображения ингредиентов в админ-панели рецепта."""

    model = RecipeIngredient
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Административная панель для управления рецептами."""

    list_display = ("id", "author", "name", "text",
                    "cooking_time", "favorites_count")
    search_fields = ("name", "cooking_time",
                     "author__email", "ingredients__name")
    list_filter = ("name", "author__username", "tags")
    inlines = (RecipeIngredientInLine,)

    @admin.display(description="В избранном")
    def favorites_count(self, obj):
        """Метод для отображения числа добавлений в избранное."""
        return obj.favorites.count()

    favorites_count.short_description = "Число добавлений в избранное"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Административная панель для управления тегами."""

    list_display = (
        "id",
        "name",
        "color",
        "slug",
    )
    search_fields = (
        "name",
        "slug",
    )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Административная панель для управления ингредиентами."""

    list_display = (
        "id",
        "name",
        "measurement_unit",
    )
    search_fields = ("^name",)


@admin.register(Subscription)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "author")
    search_fields = (
        "user__email",
        "author__email",
    )


@admin.register(FavoritRecipe)
class FavoritRecipeAdmin(admin.ModelAdmin):
    """Административная панель для управления избранными рецептами."""

    list_display = ("user", "recipe")
    search_fields = ("user", "recipe")


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Административная панель для управления списком покупок."""

    list_display = ("user", "recipe")
    search_fields = ("user", "recipe")
