import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers

from foodgram.constants import (
    ALREADY_FOLLOWING_AUTHOR, CANNOT_FOLLOW_YOURSELF,
    DUPLICATE_INGREDIENTS, DUPLICATE_TAGS, INVALID_COOKING_TIME,
    INVALID_INGREDIENT_AMOUNT, MISSING_INGREDIENTS, MISSING_TAGS,
)
from recipes.models import (
    FavoriteRecipe,
    Ingredient, IngredientAmount,
    Recipe, ShoppingCart, Tag,
)
from users.models import CustomUser, Follow


User = get_user_model()


class Base64ImageField(serializers.ImageField):

    """Сериализатор для кастомного поля картинки, декодированного в base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='photo.' + ext)

        return super().to_internal_value(data)


class ProfileSerializer(serializers.ModelSerializer):

    """Сериализатор для пользователей."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()


class FollowRecipeSerializer(serializers.ModelSerializer):

    """Сериалайзер для связи рецептов с подписками."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class FollowListSerializer(serializers.ModelSerializer):

    """Сериалайзер для подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField(read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = obj.recipes.all()
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return FollowRecipeSerializer(recipes, many=True).data

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class FollowSerializer(serializers.ModelSerializer):

    """Сериализатор для модели Follow."""

    class Meta:
        model = Follow
        fields = ('user', 'author')

    def validate(self, data):
        user = data['user']
        author = data['author']

        if user == author:
            raise serializers.ValidationError(CANNOT_FOLLOW_YOURSELF)

        if Follow.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError(ALREADY_FOLLOWING_AUTHOR)

        return data

    def to_representation(self, instance):
        return FollowListSerializer(instance.author, context=self.context).data


class IngredientSerializer(serializers.ModelSerializer):

    """Сериализатор Ингредиентов."""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class TagSerializer(serializers.ModelSerializer):

    """Сериализатор Тегов."""

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientAmountSerializer(serializers.ModelSerializer):

    """Сериализатор ингридиентов, для получения рецепта."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):

    """Сериализатор для получения рецептов."""

    tags = TagSerializer(many=True, read_only=True)
    author = ProfileSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(
        many=True, source='ingridient_list'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_is_favorited(self, obj):

        """Проверяем добавление рецепта в избранное."""

        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(
            user=request.user, recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):

        """Проверяем присутствие ингридиентов в корзине."""

        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj
        ).exists()


class AddIngredientSerializer(serializers.ModelSerializer):

    """Сериализатор  ингридиента, для добавления рецептов."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=1, max_value=200)

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):

    """Сериализатор для добавления и обновления рецептов."""

    ingredients = AddIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        )

    def validate(self, data):

        """
        Метод проверяет данные перед сохранением рецепта.
        Включает проверку уникальности тегов и ингридиентов.
        Также проверяется, что есть хотя бы один элемент.
        """

        tags = data.get('tags')
        if not tags:
            raise serializers.ValidationError({'tags': MISSING_TAGS})
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError({'tags': DUPLICATE_TAGS})

        ingredients = data.get('ingredients')
        ingredients_list = []

        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': MISSING_INGREDIENTS}
            )

        for ingredient in ingredients:
            if ingredient['id'] in ingredients_list:
                raise serializers.ValidationError(
                    {'ingredients': DUPLICATE_INGREDIENTS}
                )
            ingredients_list.append(ingredient['id'])

        if int(ingredient.get('amount')) < 1:
            raise serializers.ValidationError(
                {'ingredients': INVALID_INGREDIENT_AMOUNT}
            )

        return data

    def validate_cooking_time(self, cooking_time):

        """Метод проверяет, что время готовки не меньше одного."""

        if int(cooking_time) < 1:
            raise serializers.ValidationError(INVALID_COOKING_TIME)
        return cooking_time

    @staticmethod
    def create_ingredients(recipe, ingredients):
        ingredient_liist = []
        for ingredient_data in ingredients:
            ingredient_liist.append(
                IngredientAmount(
                    ingredient=ingredient_data.pop('id'),
                    amount=ingredient_data.pop('amount'),
                    recipe=recipe,
                )
            )
        IngredientAmount.objects.bulk_create(ingredient_liist)

    def create(self, validated_data):
        request = self.context.get('request', None)
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        IngredientAmount.objects.filter(recipe=instance).delete()
        instance.tags.set(validated_data.pop('tags'))
        ingredients = validated_data.pop('ingredients')
        self.create_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):

        """Метод преобразует представление модели при сериализации."""

        return RecipeListSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        ).data


class AddFavoriteSerializer(serializers.ModelSerializer):

    """Сериализатор для добавления рецепта в избранное."""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
