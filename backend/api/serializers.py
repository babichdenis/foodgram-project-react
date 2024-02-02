from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.fields import Base64ImageField, Hex2NameColor
from recipes.models import (Cart, FavoritRecipe, Ingredient, Recipe,
                            RecipeIngredient, Tag)
from users.models import Subscription, User


class UserListSerializer(UserSerializer):
    """
    Кастомный сериализатор,
    унаследованный от стандартного UserSerializer Djoser'а.
    Дополнительно выводит поле с информацией
    о наличии/отсутствии подписки на просматриваемого юзера.
    """
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:

            return False

        return Subscription.objects.filter(user=user, subscribing=obj).exists()


class UserPostSerializer(UserCreateSerializer):
    """Cериализатор создания пользователя."""

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


class RecipeProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецептов в профиле пользователя."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(UserSerializer):
    """Сериализатор для создания или получения подписок."""
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count',
        )
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def get_recipes(self, obj):
        """Показывает рецепты текущего пользователя."""
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = recipes[: int(recipes_limit)]
        serializer = RecipeProfileSerializer(
            recipes,
            many=True,
            read_only=True)
        return serializer.data

    def get_recipes_count(self, obj):
        """Счетчик рецептов текущего пользователя."""
        return obj.recipes.count()


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер для просмотра тегов."""
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер для просмотра ингредиентов."""
    id = serializers.ReadOnlyField()
    name = serializers.ReadOnlyField()
    measurement_unit = serializers.ReadOnlyField()

    class Meta:
        model = Ingredient
        fields = "__all__"


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для связной модели RecipeIngredient"""
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class RecipeSerializer(serializers.ModelSerializer):
    author = UserListSerializer()
    ingredients = RecipeIngredientSerializer(many=True,
                                             source='recipeingredients')
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.cart.filter(recipe=obj).exists()


class RecipePostSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецепта"""
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        required=True)

    ingredients = RecipeIngredientSerializer(many=True)
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = ('author',)

    def validate_ingredients(self, value):
        if not all(ingredient['amount'] for ingredient in value):
            raise serializers.ValidationError(
                'Количество ингредиента не может быть равным нулю'
            )
        return value

    def validate_cooking_time(self, cooking_time):
        if cooking_time < 1:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше 1 мин.')
        return cooking_time

    def create_ingredients(self, ingredients, recipe):
        RecipeIngredient.objects.bulk_create([RecipeIngredient(
            recipe=recipe,
            ingredient_id=ingredient['ingredient']['id'],
            amount=ingredient.get('amount')) for ingredient in ingredients
        ])

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            self.create_ingredients(ingredients, instance)
        if 'tags' in validated_data:
            instance.tags.set(
                validated_data.pop('tags'))
        return super().update(
            instance, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeSerializer(instance, context=context).data


class FavoritRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для добавления рецепта в избранное.
    """
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = FavoritRecipe
        fields = ('user', 'recipe')
        read_only_fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=FavoritRecipe.objects.all(),
                fields=('user', 'recipe'),
                message='Нельзя добавить рецепт в избранное дважды!'
            )
        ]


class ShoppingCartSerializer(serializers.ModelSerializer):
    """
    Сериализатор ShoppingCart.
    Проверяет, что рецепт не добавляется в ShoppingCart дважды.
    """
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = Cart
        fields = ('user', 'recipe')
        read_only_fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=Cart.objects.all(),
                fields=('user', 'recipe'),
                message='Нельзя добавить рецепт в корзину покупок дважды!'
            )
        ]
