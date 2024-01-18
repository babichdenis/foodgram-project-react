from django.contrib import admin
from django.utils.safestring import mark_safe

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

    list_editable = ('name', 'text')
    list_display = ("id",
                    "author",
                    "name",
                    "text",
                    "cooking_time", "in_favorite", "get_tags", "get_image"
                    )
    search_fields = ("name",
                     "cooking_time",
                     "author__email",
                     "ingredients__name"
                     )
    autocomplete_fields = ('author', 'tags')
    list_filter = ('author', 'tags__name')
    inlines = (RecipeIngredientInLine,
               ShoppingCartInline,
               FavoriteInline)

    def in_favorite(self, obj):
        return obj.favorited_by.count()
    in_favorite.short_description = 'В избранном'

    def get_tags(self, obj):
        return list(obj.tags.values_list('name', flat=True))
    get_tags.short_description = 'Тэги'

    def get_image(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="80" hieght="30"')
    get_image.short_description = 'Картинка'


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
    list_per_page = 30


@admin.register(Subscription)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "author")
    search_fields = (
        'author__username',
        'author__email',
        'user__username',
        'user__email'
    )
    list_filter = ('author__username', 'user__username')


@admin.register(FavoritRecipe)
class FavoritRecipeAdmin(admin.ModelAdmin):
    """Административная панель для управления избранными рецептами."""

    list_display = ('user', 'recipe')
    search_fields = ('user', 'recipe')
#    list_filter = ('recipe',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Административная панель для управления списком покупок."""

    list_display = ('user', 'recipe')
    search_fields = ('user', 'recipe')
    list_filter = ('recipe',)
