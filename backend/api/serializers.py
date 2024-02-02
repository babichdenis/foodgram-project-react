from django.core.exceptions import ObjectDoesNotExist
from djoser.serializers import UserCreateSerializer, UserSerializer
from foodgram import constants
from rest_framework import serializers, status

from api.fields import Base64ImageField, Hex2NameColor
from recipes.models import (Cart, FavoritRecipe, Ingredient, Recipe,
                            RecipeIngredient, Tag)
from users.models import Subscription, User


class UserListSerializer(UserSerializer):
    """Cериализатор просмотра профиля пользователя"""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        """Проверяет подписку на текущего пользователя"""
        user = self.context.get('request').user
        if user.is_anonymous or (user == obj):
            return False
        return user.subscriber.filter(author=obj).exists()


class UserPostSerializer(UserCreateSerializer):
    """Cериализатор создания пользователя."""

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class RecipeProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецептов в профиле пользователя."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubscribeSerializer(UserSerializer):
    """Сериализатор для создания или получения подписок."""
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = ('email',
                            'username',
                            'first_name',
                            'last_name'
                            )

    def get_is_subscribed(self, obj):
        """Проверяет подписку на текущего пользователя."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.subscriber.filter(author=obj).exists()

    def get_recipes(self, obj):
        """Показывает рецепты текущего пользователя."""
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = recipes[: int(recipes_limit)]
        serializer = RecipeProfileSerializer(recipes,
                                             many=True, read_only=True)
        return serializer.data

    def get_recipes_count(self, obj):
        """Счетчик рецептов текущего пользователя."""
        return obj.recipes.count()

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if Subscription.objects.filter(author=author, user=user).exists():
            raise serializers.ValidationError(
                detail='Подписка уже существует',
                code=status.HTTP_400_BAD_REQUEST,
            )
        if user == author:
            raise serializers.ValidationError(
                detail='Нельзя подписаться на самого себя',
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер для просмотра тегов."""

    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер для просмотра ингредиентов."""

    class Meta:
        model = Ingredient
        fields = "__all__"
        read_only_fields = ("__all__",)


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
        read_only_fields = ('name', 'measurement_unit')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов."""

    author = UserListSerializer()
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipeingredients'
    )
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = (
            'is_favorited',
            'is_in_shopping_cart',
            'tags'
        )

    def get_is_favorited(self, obj):
        """Проверка - находится ли рецепт в избранном."""

        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        """Проверка - находится ли рецепт в списке  покупок."""

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

    ingredients = RecipeIngredientSerializer(
        many=True
    )
    image = Base64ImageField(
        required=True
    )
    author = UserSerializer()

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = ('author',)

    def validate_image(self, image):
        if not image:
            raise serializers.ValidationError(
                'Поле изображения не может быть пустым.'
            )
        return image

    def validate_cooking_time(self, cooking_time):
        if cooking_time < 1:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше 1 мин.')
        return cooking_time

    def create_ingredients(self, ingredients, recipe):
        try:
            RecipeIngredient.objects.bulk_create([
                RecipeIngredient(
                    ingredient=Ingredient.objects.get(pk=ingredient.get('id')),
                    recipe=recipe,
                    amount=ingredient.get('amount'),
                ) for ingredient in ingredients]
            )
        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                'Указан не существующий ингредиент!'
            )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients', [])
        tags = validated_data.pop('tags', [])
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        """ Обновление рецепта. """
        instance.tags.clear()
        instance.tags.set(validated_data.pop('tags'))
        RecipeIngredient.objects.filter(recipe=instance).delete()
        self.__create_ingredients(
            recipe=instance,
            ingredients=validated_data.pop('ingredients')
        )
        super().update(instance, validated_data)
        return instance

    def to_representation(self, instance):
        """Заменяет сериализатор выдачи на RecipeSerializer."""

        if isinstance(instance, Recipe):
            serializer = RecipeSerializer(instance)
        return serializer.data

    def validate(self, data):
        """ Валидация различных данных на уровне сериализатора. """
        ingredients = data.get('ingredients')
        errors = []
        if not ingredients:
            errors.append('Добавьте минимум один ингредиент для рецепта.')
        added_ingredients = []
        for ingredient in ingredients:
            if int(ingredient['amount']) < constants.MIN_INGREDIENT_AMOUNT:
                errors.append(
                    f'Количество ингредиента с id {ingredient["id"]} должно '
                    f'быть целым и не меньше '
                    f'{constants.MIN_INGREDIENT_AMOUNT}.'
                )
            if ingredient['id'] in added_ingredients:
                errors.append(
                    'Дважды один тот же ингредиент в рецепт поместить нельзя.'
                )
            added_ingredients.append(ingredient['id'])
        cooking_time = data.get('cooking_time')
        if cooking_time < constants.MIN_COOKING_TIME:
            errors.append(
                f'Время приготовления должно быть не меньше '
                f'{constants.MIN_COOKING_TIME} минут(ы).'
            )
        if cooking_time > constants.MAX_COOKING_TIME:
            errors.append(
                f'Время приготовления должно быть не больше '
                f'{constants.MAX_COOKING_TIME} минут(ы).'
            )
        if errors:
            raise serializers.ValidationError({'errors': errors})
        data['ingredients'] = ingredients
        return data


class FavoritRecipeSerializer(RecipeSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cooking_time', 'image')
        read_only_fields = ('name', 'cooking_time', 'image')

    def validate(self, data):
        recipe = self.instance
        user = self.context.get('request').user
        if FavoritRecipe.objects.filter(recipe=recipe, user=user).exists():
            raise serializers.ValidationError(
                detail='Рецепт уже в избранных',
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data


class CartSerializer(RecipeSerializer):
    """Сериализатор добавления рецепта в корзину"""

    class Meta:
        model = Cart
        fields = ("id", "name", "image", "cooking_time")
        read_only_fields = ('name', 'cooking_time', 'image')

    def validate(self, data):
        user = self.context['request'].user
        recipe = data['recipe']
        cart = user.shopingcarts.filter(recipe=recipe).exists()

        if self.context.get('request').method == 'POST' and cart:
            raise serializers.ValidationError(
                'Этот рецепт уже добавлен в корзину'
            )
        if self.context.get('request').method == 'DELETE' and not cart:
            raise serializers.ValidationError(
                'Этот рецепт отсутствует в корзине'
            )
        return data
