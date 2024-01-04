import base64
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from django.contrib.auth.password_validation import validate_password
from django.core.files.base import ContentFile

from recipes.models import (FavoriteRecipe, Ingredient, IngredientInRecipe,
                            Recipe, ShoppingCart, Tag)
from users.models import Subscribe, User


class SignupSerializer(UserCreateSerializer):
    """Сериализатор для модели регистрации."""

    email = serializers.EmailField(
        required=True,
        allow_blank=False,
        trim_whitespace=True,
        max_length=254
    )
    username = serializers.RegexField(
        required=True,
        regex=r'^[\w.@+-]+\Z',
        max_length=150)
    first_name = serializers.CharField(
        max_length=150
    )
    last_name = serializers.CharField(
        max_length=150
    )
    password = serializers.CharField(
        write_only=True
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )

    def validate(self, data):
        if data.get('username') == 'me':
            raise serializers.ValidationError(
                'Нельзя использовать имя me. Придумайте другой username.'
            )
        if User.objects.filter(username=data.get('username')):
            raise serializers.ValidationError(
                'Пользователь с таким username уже существует. '
                'Придумайте другой username.'
            )
        if User.objects.filter(email=data.get('email')):
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует.'
            )

        validate_password(data.get('password'))

        return data


class CustomUserSerializer(UserSerializer):
    """Сериализатор для модели юзера."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        current_user = self.context.get('request').user
        if current_user.is_anonymous:
            return False
        return Subscribe.objects.filter(
            subscribing=obj, subscriber=current_user).exists()


class Base64ImageField(serializers.ImageField):
    """"Сериализатор для декодирования картинки из строки base64"""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class SubscriptionSerializer(CustomUserSerializer):
    """Сериализатор для отображения подписок"""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='recipes.count',
        read_only=True
    )

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeShortSerializer(recipes, many=True, read_only=True)
        return serializer.data

    class Meta:
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
        model = User
        read_only_fields = ('email', 'username', 'first_name', 'last_name')


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор для короткого отображения рецепта"""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели тегов."""

    class Meta:
        fields = (
            'id',
            'name',
            'color',
            'slug')
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ингридиентов."""

    class Meta:
        fields = (
            'id',
            'name',
            'measurement_unit'
        )
        model = Ingredient


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ингридиент-рецепт."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )
        model = IngredientInRecipe


class IngredientInRecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ингридиент-рецепт."""

    id = serializers.IntegerField(write_only=True)

    class Meta:
        fields = (
            'id',
            'amount'
        )
        model = IngredientInRecipe


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для модели рецептов(для создания рецепта)."""
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = IngredientInRecipeWriteSerializer(many=True)
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)

    class Meta:
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'image',
            'name',
            'text',
            'cooking_time'
        )
        model = Recipe

    def validate(self, data):
        for field in (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        ):
            if not self.initial_data.get(field):
                raise serializers.ValidationError(
                    f'Не заполнено поле "{field}"!')
        ingredients = self.initial_data['ingredients']
        ingredients_list = []
        for current_ingredient in ingredients:
            try:
                ingredient = Ingredient.objects.get(
                    id=current_ingredient['id']
                )
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError(
                    'Такой ингридиент не существует!'
                )
            if ingredient in ingredients_list:
                raise serializers.ValidationError(
                    'Ингридиенты не могут повторяться!'
                )
            ingredients_list.append(ingredient)
        return data

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.add(*tags)

        ingredient_list = []
        for ingredient_data in ingredients_data:
            ingredient_list.append(
                IngredientInRecipe(
                    recipe=recipe,
                    ingredient=Ingredient.objects.get(
                        id=ingredient_data['id']
                    ),
                    amount=ingredient_data['amount']
                )
            )
        IngredientInRecipe.objects.bulk_create(ingredient_list)
        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        instance.tags.clear()
        tags = validated_data.pop('tags')
        instance.tags.add(*tags)
        instance.ingredients.clear()
        ingredients_data = validated_data.pop('ingredients')
        ingredient_list = []
        for ingredient_data in ingredients_data:
            ingredient_list.append(
                IngredientInRecipe(
                    recipe=instance,
                    ingredient=Ingredient.objects.get(
                        id=ingredient_data['id']
                    ),
                    amount=ingredient_data['amount']
                )
            )
        IngredientInRecipe.objects.bulk_create(ingredient_list)
        instance.save()
        return instance

    def to_representation(self, recipe):
        serializer = RecipeReadSerializer(
            recipe, context=self.context
        )
        return serializer.data


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для модели рецептов(для чтения рецепта)."""

    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        source='ingredients_amount', many=True, read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
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
            'cooking_time',
        )
        model = Recipe

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(recipe=obj, user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(recipe=obj, user=user).exists()
