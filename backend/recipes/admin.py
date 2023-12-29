from django.contrib import admin

from .models import (FavoriteRecipe, Ingredient, Recipe, RecipeIngredient,
                     ShoppingList, Tag)


class RecipeIngredientInline(admin.TabularInline):
    """Inline для отображения ингредиентов в админ-панели рецепта."""

    model = RecipeIngredient
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Административная панель для управления рецептами."""

    inlines = (RecipeIngredientInline,)
    list_display = ("name", "author", "favorites_count")
    list_filter = ("author", "name", "tags")
    filter_horizontal = ("tags",)
    search_fields = ("name", "author")

    def favorites_count(self, obj):
        """Метод для отображения числа добавлений в избранное."""
        return obj.favorited_by.count()

    favorites_count.short_description = "Число добавлений в избранное"


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Административная панель для управления ингредиентами."""

    list_display = ("name", "measurement_unit")
    list_filter = ("name",)
    search_fields = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Административная панель для управления тегами."""

    list_display = ("name", "color", "slug")
    list_filter = ("name", "color")
    search_fields = ("name", "color")


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    """Административная панель для управления избранными рецептами."""

    list_display = ("user", "recipe")
    search_fields = ("user", "recipe")


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    """Административная панель для управления списком покупок."""

    list_display = ("user", "recipe")
    search_fields = ("user", "recipe")
