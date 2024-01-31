from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from foodgram.constants import MAX_PAGE_SIZE

from recipes.models import (Cart, FavoritRecipe, Ingredient, Recipe,
                            RecipeIngredient, Tag)
from users.models import Subscription

admin.site.empty_value_display = "Не задано"


class RecipeIngredientInLine(admin.TabularInline):
    """Inline для отображения ингредиентов в админ-панели рецепта."""

    model = RecipeIngredient
    extra = 0


class FavoriteInline(admin.TabularInline):
    """Inline для отображения избранных в админ-панели рецепта."""

    model = FavoritRecipe
    extra = 0


class ShoppingCartInline(admin.TabularInline):
    """Inline для отображения покупок админ-панели рецепта."""

    model = Cart
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Административная панель для управления рецептами."""

    list_editable = ("name",)
    list_display = (
        "get_image",
        "name",
        "ingredients_list",
        "in_favorite",
        "cooking_time",
        "get_tags",
        "author",
    )
    search_fields = (
        "name",
        "cooking_time",
        "author__email",
        "ingredients__name" "tags__name",
    )
    list_filter = ("author", "tags__name")
    inlines = (RecipeIngredientInLine, ShoppingCartInline, FavoriteInline)

    @admin.display(description="Добавили в избранное")
    def in_favorite(self, obj):
        """Показывает сколько раз рецепт добавлен в избранное."""
        return obj.favorites.count()

    in_favorite.short_description = "В избранном"

    @admin.display(description="Теги")
    def get_tags(self, obj):
        """Получение тегов рецепта."""
        return list(obj.tags.values_list("name", flat=True))

    get_tags.short_description = "Тэги"

    def get_image(self, obj):
        """Получение картинок рецепта."""
        return mark_safe(f'<img src={obj.image.url} width="80" hieght="30"')

    get_image.short_description = "Картинка"

    @admin.display(description="Ингридиенты")
    def ingredients_list(self, obj):
        """Получение ингридиентов рецепта."""
        return "\n".join((
            ingredient.name for ingredient in obj.ingredients.all()))


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Административная панель для управления тегами."""

    list_display = (
        "color_code",
        "color",
        "slug",
    )
    search_fields = (
        "name",
        "color",
        "color_code",
    )
    list_editable = ("slug",)

    @admin.display(description="Colored")
    def color_code(self, obj: Tag):
        return format_html(
            '<span style="color: #{};">{}</span>', obj.color[1:], obj.name
        )

    color_code.short_description = "Название тэга"
#    list_per_page = MAX_PAGE_SIZE


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Административная панель для управления ингредиентами."""

    list_display = (
        "id",
        "name",
        "measurement_unit",
    )
    search_fields = ("^name",)
#    list_per_page = MAX_PAGE_SIZE


@admin.register(Subscription)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "author")
    search_fields = (
        "author__username",
        "author__email",
        "user__username",
        "user__email",
    )
    list_filter = ("author__username", "user__username")
    list_per_page = MAX_PAGE_SIZE


@admin.register(FavoritRecipe)
class FavoritRecipeAdmin(admin.ModelAdmin):
    """Административная панель для управления избранными рецептами."""

    list_display = ("user", "recipe")
    search_fields = ("user__username", "recipe__name")
    list_editable = ("recipe",)
    list_filter = ("recipe",)
    list_per_page = MAX_PAGE_SIZE


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Административная панель для управления списком покупок."""

    list_display = ("user", "recipe")
    list_editable = ("recipe",)
    search_fields = ("recipe",)
    list_filter = ("recipe",)
    list_per_page = MAX_PAGE_SIZE
