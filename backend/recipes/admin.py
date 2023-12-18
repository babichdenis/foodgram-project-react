from django.contrib import admin

from .models import (
    Ingredient,
    Tag,
    IngredientRecipe,
    Recipe,
    TagRecipe,
    Favorite
)

admin.site.empty_value_display = "Не задано"


class TagRecipeAdminInline(admin.TabularInline):
    model = TagRecipe
    extra = 1


class IngredientRecipeAdminInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 1


@admin.register(Ingredient)
class AdminIngredient(admin.ModelAdmin):
    """Административная панель для управления ингредиентами."""

    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)
    inlines = (IngredientRecipeAdminInline,)


@admin.register(Tag)
class AdminTag(admin.ModelAdmin):
    """Административная панель для управления тегами."""
    inlines = (TagRecipeAdminInline,)
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'color')
    list_filter = ('name', 'color')


@admin.register(Recipe)
class AdminRecipe(admin.ModelAdmin):
    """Административная панель для управления рецептами."""

    inlines = (IngredientRecipeAdminInline, TagRecipeAdminInline)
    list_display = ('name',
                    'author',
                    'cooking_time',
                    'followers'
                    )
    list_filter = ('author', 'name', 'tags')
    search_fields = ('name', 'author')

    def followers(self, obj):
        result = Favorite.objects.filter(recipe=obj)
        return len(list(result))

    followers.short_description = "B избранном"


@admin.register(Favorite)
class AdminFavorite(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe')
