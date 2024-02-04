from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from foodgram.constants import Constants

from recipes.models import (Cart, FavoritRecipe, Ingredient, Recipe,
                            RecipeIngredient, Tag)

admin.site.empty_value_display = "Не задано"


class BaseFoodgramAdmin(admin.ModelAdmin):
    """Базовая админ-модель с пагинацией."""

    list_per_page = Constants.MAX_PAGE_SIZE
    list_max_show_all = Constants.MAX_PAGE_SIZE


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
class RecipeAdmin(BaseFoodgramAdmin):
    """Административная панель для управления рецептами."""

    list_display = (
        "id",
        "get_image",
        "name",
        "ingredients_list",
        "in_favorite",
        "cooking_time",
        "get_tags",
        "author",
        "pub_date",
    )
    search_fields = (
        "name",
        "cooking_time",
        "author__email",
        "ingredients__name",
        "tags__name",
    )
    list_filter = ("author", "tags__name")
    list_display_links = ('name', 'id')
    date_hierarchy = 'pub_date'
    filter_horizontal = ('tags',)
    inlines = (RecipeIngredientInLine, ShoppingCartInline, FavoriteInline)

    @admin.display(description="Добавили в избранное")
    def in_favorite(self, obj):
        """Счетчик добавлений рецепта в избранное."""
        return obj.favorites.count()

    @admin.display(description='Теги')
    def get_tags(self, recipe: Recipe):
        """Список ингредиентов рецепта."""
        return list(recipe.tags.only('name'))

    get_tags.short_description = "Тэги"

    def get_image(self, obj):
        """Получение картинок рецепта."""
        return mark_safe(f'<img src={obj.image.url} width="80" hieght="30"')

    get_image.short_description = "Картинка"

    @admin.display(description='Ингредиенты')
    def ingredients_list(self, recipe: Recipe):
        """Список ингредиентов рецепта."""
        return list(recipe.ingredients.only('name'))


@admin.register(Tag)
class TagAdmin(BaseFoodgramAdmin):
    """Административная панель для управления тегами."""

    list_display = (
        "id",
        "name",
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
    list_display_links = ('name', 'id')

    @admin.display(description="Colored")
    def color_code(self, obj: Tag):
        return format_html(
            '<span style="color: #{};">{}</span>', obj.color[1:], obj.name
        )

    color_code.short_description = "Название тэга"


@admin.register(Ingredient)
class IngredientAdmin(BaseFoodgramAdmin):
    """Административная панель для управления ингредиентами."""

    fields = (('name', 'measurement_unit'),)
    list_display = ('id', 'name', 'measurement_unit')
    list_display_links = ('name', 'id')
    search_fields = ('name', 'id')


@admin.register(FavoritRecipe)
class FavoritRecipeAdmin(BaseFoodgramAdmin):
    """Административная панель для управления избранными рецептами."""

    list_display = ('user', 'recipe', 'added_date')
    search_fields = ('user__username', 'recipe__name')
    list_editable = ('recipe',)
    list_filter = ('recipe',)


@admin.register(Cart)
class CartAdmin(BaseFoodgramAdmin):
    """Административная панель для управления списком покупок."""

    list_display = ('id', '__str__', 'user', 'recipe', 'added_date')
    list_display_links = ('__str__', 'id')
    search_fields = ('recipe__name', 'user__username')
