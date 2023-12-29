from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import BaseFilterBackend
from rest_framework.pagination import BasePagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from typing import Optional

from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
                            RecipeIngredient, ShoppingList, Tag)

from django.db.models import Sum
from django.db.models.query import QuerySet
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from .filters import IngredientFilter, RecipeFilter
from .permissions import OwnerOnlyPermission
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeGETSerializer,
                          ShoppingListSerializer, SubscriptionCreateSerializer,
                          SubscriptionSerializer, TagSerializer,
                          UserGETSerializer)
from .utils import (add_favorite_or_shopping_list, generate_shopping_list_pdf,
                    remove_favorite_or_shopping_list)
from users.models import Subscribe, User


class MeView(APIView):
    """Представление для получения данных о текущем пользователе."""

    permission_classes: tuple[type[IsAuthenticated]] = (IsAuthenticated,)

    def get(self, request, *args, **kwargs) -> Response:
        """Получение данных о текущем пользователе."""
        serializer: type[UserGETSerializer] = UserGETSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubscribeView(APIView):
    """Представление для подписки и отписки от авторов."""

    permission_classes: tuple[type[IsAuthenticated]] = (IsAuthenticated,)

    def get_user_author(self, request, pk: int) -> tuple[User, User]:
        """Получение текущего пользователя и автора по идентификатору."""
        user: User = request.user
        author: User = get_object_or_404(User, id=pk)
        return user, author

    def post(self, request, pk: int = None) -> Response:
        """Обработка HTTP-запроса POST для создания подписки на автора."""
        user, author = self.get_user_author(
            request, pk
        )  # type: tuple[User, User]

        serializer: type[
            SubscriptionCreateSerializer
        ] = SubscriptionCreateSerializer(
            data={"user": user.id, "author": author.id},
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk: int = None) -> Response:
        """Обработка HTTP-запроса DELETE для удаления подписки на автора."""
        user, author = self.get_user_author(
            request, pk
        )  # type: tuple[User, User]

        if subscribe := Subscribe.objects.filter(
            user=user, author=author
        ).first():
            subscribe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {"ошибка": "вы не подписаны на этого автора."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class SubscriptionsListView(generics.ListAPIView):
    """Список подписок пользователя."""

    serializer_class: type[SubscriptionSerializer] = SubscriptionSerializer
    permission_classes: tuple[type[IsAuthenticated]] = (IsAuthenticated,)

    def get_queryset(self) -> QuerySet[User]:
        """Получение списка подписок пользователя."""
        user: User = self.request.user
        return User.objects.filter(following__user=user)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для просмотра тегов."""

    queryset: QuerySet[Tag] = Tag.objects.all()
    serializer_class: type[TagSerializer] = TagSerializer
    permission_classes: tuple[type[AllowAny]] = (AllowAny,)
    pagination_class: type[BasePagination] = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для просмотра ингредиентов."""

    queryset: QuerySet[Ingredient] = Ingredient.objects.all()
    serializer_class: type[IngredientSerializer] = IngredientSerializer
    permission_classes: tuple[type[AllowAny]] = (AllowAny,)
    filter_backends: tuple[type[BaseFilterBackend]] = (DjangoFilterBackend,)
    filterset_class: type[IngredientFilter] = IngredientFilter
    pagination_class: type[BasePagination] = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Представление для просмотра и редактирования рецептов."""

    permission_classes: tuple[type[OwnerOnlyPermission]] = (
        OwnerOnlyPermission,
    )
    filter_backends: tuple[type[BaseFilterBackend]] = (DjangoFilterBackend,)
    filterset_class: type[RecipeFilter] = RecipeFilter

    def get_queryset(self) -> QuerySet[Recipe]:
        """Получает набор запросов для модели Recipe."""
        user_id: Optional[int] = self.request.user.id
        queryset: QuerySet[Recipe] = Recipe.objects.select_related(
            "author"
        ).prefetch_related("tags", "ingredients")

        if user_id is not None:
            queryset: QuerySet[Recipe] = queryset.favorited(
                user_id
            ).in_shopping_cart(user_id)

        return queryset

    def get_serializer_class(self):
        """Определение, какой сериализатор использовать."""
        if self.action in ("list", "retrieve"):
            return RecipeGETSerializer
        return RecipeCreateSerializer

    @action(
        detail=True,
        methods=("post", "delete"),
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk: int = None) -> Response:
        """Добавление или удаление рецепта из избранного."""
        user: User = request.user

        if request.method == "POST":
            return add_favorite_or_shopping_list(
                request, user, FavoriteRecipe, FavoriteSerializer, pk
            )

        elif request.method == "DELETE":
            return remove_favorite_or_shopping_list(user, FavoriteRecipe, pk)

    @action(
        detail=True,
        methods=("post", "delete"),
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk: int = None) -> Response:
        """Добавление или удаление рецепта из списка покупок."""
        user: User = request.user

        if request.method == "POST":
            return add_favorite_or_shopping_list(
                request, user, ShoppingList, ShoppingListSerializer, pk
            )

        elif request.method == "DELETE":
            return remove_favorite_or_shopping_list(user, ShoppingList, pk)

    @action(
        detail=False,
        methods=("get",),
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request) -> HttpResponse:
        """Загрузка списка покупок ингредиентов в виде текстового файла."""
        user: User = request.user
        recipes_in_shopping_list: QuerySet[RecipeIngredient] = (
            RecipeIngredient.objects.filter(
                recipe__in_shopping_lists__user=user
            )
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(total_amount=Sum("amount"))
        )

        pdf_buffer: HttpResponse = generate_shopping_list_pdf(
            recipes_in_shopping_list
        )

        response: HttpResponse = HttpResponse(
            pdf_buffer.getvalue(), content_type="application/pdf"
        )
        response[
            "Content-Disposition"
        ] = 'attachment; filename="shopping_list.pdf"'
        return response
