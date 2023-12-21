import django_filters

from recipes.models import Ingredient, Recipe, Tag


class RecipeFilter(django_filters.FilterSet):
    """
    Фильтр для модели Recipe.

    Фильтрует рецепты по автору, тегам, наличию в списке покупок и избранности.
    """

    tags = django_filters.filters.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        to_field_name="slug",
        queryset=Tag.objects.all(),
    )
    is_in_shopping_cart = django_filters.NumberFilter(
        method="filter_is_in_shopping_cart"
    )
    is_favorited = django_filters.NumberFilter(method="filter_is_favorited")

    class Meta:
        model = Recipe
        fields = ("author", "tags", "is_favorited", "is_in_shopping_cart")

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтрует рецепты по наличию в списке покупок."""
        if self.request.user.is_authenticated and value:
            return queryset.filter(in_shopping_lists__user=self.request.user)
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        """Фильтрует рецепты по наличию в списке избранных."""
        if self.request.user.is_authenticated and value:
            return queryset.filter(favorited_by__user=self.request.user)
        return queryset


class IngredientFilter(django_filters.FilterSet):
    """
    Фильтр для ингредиентов.

    Фильтрует ингредиенты по начальным буквам в названии.
    """

    name = django_filters.CharFilter(
        lookup_expr="icontains",
    )

    class Meta:
        model = Ingredient
        fields = ("name",)