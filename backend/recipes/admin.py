from django.contrib import admin

from .models import Ingredient, Tag, IngredientRecipe, Recipe, TagRecipe

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

    inlines = (IngredientRecipeAdminInline,)
#    list_display = ("name", "author", "favorites_count")
    list_display = ("name", "author")
    list_filter = ("author", "name", "tags")
    search_fields = ("name", "author")

#    def favorites_count(self, obj):
#        """Метод для отображения числа добавлений в избранное."""
#        return obj.favorited_by.count()

#    favorites_count.short_description = "Число добавлений в избранное"

