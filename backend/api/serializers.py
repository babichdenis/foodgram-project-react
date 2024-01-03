import base64

import djoser.serializers
from django.core.files.base import ContentFile
from foodgram.constants import MIN_AMOUNT, MIN_COOKING_TIME
from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
                            RecipeIngredient, ShoppingList, Tag)
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from users.models import Subscribe, User

from .utils import create_update_ingredients


class Base64ImageField(serializers.ImageField):
    """
    Пользовательское поле сериализатора для обработки изображений.
    """

    def to_internal_value(self, data):
        """
        Преобразует данные изображения в формате base64 в объект `ContentFile`.
        """
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)

        return super().to_internal_value(data)


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения информации о рецептах."""

    image = Base64ImageField(read_only=True)
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        fields = ("id", "name", "image", "cooking_time")
        model = Recipe


class UserGETSerializer(djoser.serializers.UserSerializer):
    """Сериализатор для чтения информации о пользователях."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )
        model = User

    def get_is_subscribed(self, obj):
        """Возвращает значение поля is_subscribed."""
        request = self.context.get("request")

        if request and not request.user.is_anonymous:
            user = request.user
            return user.followers.filter(author=obj).exists()
        return False


class UserCreateSerializer(djoser.serializers.UserCreateSerializer):
    """Сериализатор для создания новых пользователей."""

    class Meta:
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
        )
        model = User


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок пользователя."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)
    email = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    first_name = serializers.ReadOnlyField()
    last_name = serializers.ReadOnlyField()

    class Meta:
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )
        model = User

    def get_is_subscribed(self, obj):
        """Возвращает значение поля is_subscribed."""
        request = self.context.get("request")

        if request and not request.user.is_anonymous:
            user = request.user
            return user.followers.filter(author=obj).exists()

        return False

    def get_recipes_count(self, obj):
        """Возвращает количество рецептов пользователя."""
        return Recipe.objects.filter(author=obj).count()

    def get_recipes(self, obj):
        """Возвращает информацию о рецептах пользователя."""
        request = self.context.get("request")
        recipes_limit = request.query_params.get("recipes_limit", None)

        if recipes_limit is not None:
            recipes = Recipe.objects.filter(author=obj)[: int(recipes_limit)]
        else:
            recipes = Recipe.objects.filter(author=obj)

        serializer = RecipeReadSerializer(
            recipes, many=True, context=self.context
        )
        return serializer.data


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания подписок пользователя."""

    class Meta:
        model = Subscribe
        fields = "__all__"
        validators = [
            UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=("user", "author"),
                message="Вы уже подписаны",
            )
        ]

    def validate(self, obj):
        """Проверяет валидность данных."""
        user = self.context.get("request").user
        author = obj["author"]

        if user == author:
            raise serializers.ValidationError(
                "Нельзя подписываться на самого себя"
            )

        return obj

    def to_representation(self, instance):
        """Преобразует объект подписки в представление."""
        request = self.context.get("request")
        return SubscriptionSerializer(
            instance.author, context={"request": request}
        ).data


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""

    class Meta:
        fields = "__all__"
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""

    class Meta:
        fields = "__all__"
        model = Ingredient


class RecipeIngredientGETSerializer(serializers.ModelSerializer):
    """Сериализатор для получения данныъ о связанных ингредиентах рецепта."""

    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )
        model = RecipeIngredient


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания связанных ингредиентов рецепта."""

    id = serializers.IntegerField()

    class Meta:
        fields = (
            "id",
            "amount",
        )
        model = RecipeIngredient


class RecipeGETSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения информации о рецептах."""

    author = UserGETSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientGETSerializer(
        many=True, read_only=True, source="recipes"
    )
    is_favorited = serializers.BooleanField(read_only=True, default=False)
    is_in_shopping_cart = serializers.BooleanField(
        read_only=True, default=False
    )

    class Meta:
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        model = Recipe


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецептов."""

    image = Base64ImageField(required=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, required=True
    )
    ingredients = RecipeIngredientCreateSerializer(many=True, required=True)

    class Meta:
        fields = (
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
        )
        model = Recipe

    def validate(self, obj):
        """Проверяет валидность данных."""
        ingredients = obj.get("ingredients", [])
        tags = obj.get("tags", [])
        cooking_time = obj.get("cooking_time", 0)

        if not tags:
            raise serializers.ValidationError(
                "Рецепт должен содержать как минимум один тэг"
            )
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError("Тэги не должны повторяться")

        if not ingredients:
            raise serializers.ValidationError(
                "Рецепт должен содержать как минимум один ингредиент"
            )
        ingredients_list = set()
        for ingredient in ingredients:
            ingredient_id = ingredient.get("id")
            amount = ingredient.get("amount")
            if amount < MIN_AMOUNT:
                raise serializers.ValidationError(
                    f"Количество ингредиента не может быть меньше {MIN_AMOUNT}"
                )
            if not Ingredient.objects.filter(id=ingredient_id).exists():
                raise serializers.ValidationError("Ингредиент не существует")
            if ingredient_id in ingredients_list:
                raise serializers.ValidationError(
                    "Ингредиент уже добавлен в рецепт"
                )
            ingredients_list.add(ingredient_id)

        if cooking_time < MIN_COOKING_TIME:
            raise serializers.ValidationError(
                f"Время готовки не может быть менее {MIN_COOKING_TIME} мин"
            )

        return obj

    def create(self, validated_data):
        """Создает новый рецепт."""
        user = self.context.get("request").user
        ingredients_data = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")

        recipe = Recipe.objects.create(author=user, **validated_data)

        recipe.tags.set(tags)

        create_update_ingredients(recipe, ingredients_data)

        return recipe

    def update(self, instance, validated_data):
        """Обновляет рецепт."""
        instance.image = validated_data.get("image", instance.image)
        instance.name = validated_data.get("name", instance.name)
        instance.text = validated_data.get("text", instance.text)
        instance.cooking_time = validated_data.get(
            "cooking_time", instance.cooking_time
        )
        ingredients_data = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")

        instance.tags.clear()
        instance.tags.set(tags)

        RecipeIngredient.objects.filter(recipe=instance).delete()

        create_update_ingredients(instance, ingredients_data)

        instance.save()
        return instance

    def to_representation(self, instance):
        """Преобразует объект рецепта в сериализованный формат."""
        return RecipeGETSerializer(instance, context=self.context).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Серилизатор для избранных рецептов."""

    class Meta:
        fields = ("recipe", "user")
        model = FavoriteRecipe

    def validate(self, obj):
        """Проверяет валидность данных."""
        user = obj["user"]

        if user.favorite_recipes.filter(recipe=obj["recipe"]).exists():
            raise serializers.ValidationError(
                "Рецепт уже добавлен в избранное."
            )
        return obj

    def to_representation(self, instance):
        """Преобразует объект избранного рецепта в сериализованный формат."""
        request = self.context.get("request")
        return RecipeReadSerializer(
            instance.recipe, context={"request": request}
        ).data


class ShoppingListSerializer(serializers.ModelSerializer):
    """Серилизатор для списка покупок."""

    class Meta:
        fields = ("recipe", "user")
        model = ShoppingList

    def validate(self, obj):
        """Проверяет валидность данных."""
        user = obj["user"]

        if user.shopping_lists.filter(recipe=obj["recipe"]).exists():
            raise serializers.ValidationError("Рецепт уже добавлен в корзину")

        return obj

    def to_representation(self, instance):
        """Преобразует объект списка покупок в сериализованный формат."""
        request = self.context.get("request")
        return RecipeReadSerializer(
            instance.recipe, context={"request": request}
        ).data
