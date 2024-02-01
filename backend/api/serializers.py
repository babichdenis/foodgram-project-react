from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

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

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = ('author',)

    def validate_ingredients(self, value):
        """Проверяет, чтобы ингредиенты для одного рецепта не повтоялись."""
        unique_ingredients_pk = []
        for ingredient in value:
            current_pk = ingredient['ingredient'].pk
            if current_pk in unique_ingredients_pk:
                raise serializers.ValidationError(
                    'Ингредиенты в списке не должны повторяться.'
                )
            unique_ingredients_pk.append(current_pk)
        return value

    def validate_image(self, image):
        if not image:
            raise serializers.ValidationError(
                'Поле изображения не может быть пустым.'
            )
        return image

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError(
                'Теги должны быть заданы.'
            )
        if len(set(tags)) != len(tags):
            raise serializers.ValidationError(
                'Такой тег уже в рецепте.'
            )

        return tags

    def validate_cooking_time(self, cooking_time):
        if cooking_time < 1:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше 1 мин.')
        return cooking_time

    @staticmethod
    def create_ingredients(recipe, ingredients):
        ingredients.sort(
            key=lambda ingredient: ingredient.get('ingredient').name
        )
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    recipe=recipe,
                    ingredient_id=ingredient.get('ingredient').id,
                    amount=ingredient.get('amount')
                )
                for ingredient in ingredients
            ]
        )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):

        if 'tags' in validated_data:
            instance.tags.clear()
            instance.tags.set(validated_data.pop('tags'))
        else:
            raise ValidationError('Отсутствует поле tags.')

        if 'recipe_ingredients' in validated_data:
            RecipeIngredient.objects.filter(recipe=instance).delete()
            ingredients = validated_data.pop('recipe_ingredients')
            self.create_ingredients(instance, ingredients)
        else:
            raise ValidationError('Отсутствует поле ingredients.')

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Заменяет сериализатор выдачи на RecipeSerializer."""

        request = self.context.get('request')
        context = {'request': request}
        return RecipeSerializer(instance, context=context).data


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

    class Meta(RecipeSerializer.Meta):
        fields = ("id", "name", "image", "cooking_time")
        read_only_fields = ('name', 'cooking_time', 'image')

    def validate(self, data):
        recipe = self.instance
        user = self.context.get('request').user
        if Cart.objects.filter(recipe=recipe, user=user).exists():
            raise serializers.ValidationError(
                detail='Рецепт уже в корзине',
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data
