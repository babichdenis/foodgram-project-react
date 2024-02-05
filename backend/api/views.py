
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.filters import IngredientSearchFilter, RecipeFilter
from api.pagination import Pagination
from api.serializers import (CartSerializer, FavoritesSerializer,
                             IngredientSerializer, RecipeCreateSerializer,
                             RecipeReadSerializer, TagSerializer)
from api.services import ShoppingListCreator
from recipes.models import Cart, FavoritRecipe, Ingredient, Recipe, Tag
from users.permissions import IsAuthorOrAdminOrHigherOrReadOnly


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Вьюсет для представления ингредиентов.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [IngredientSearchFilter, ]
    search_fields = ('^name',)


class RecipeViewSet(ModelViewSet):
    """
    Вьюсет для представления, создания, редактирования и удаления рецептов.
    """
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrAdminOrHigherOrReadOnly,
                          IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = RecipeFilter
    pagination_class = Pagination

    def update(self, request: Request, *args, **kwargs):
        if request.method == 'PUT':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED,
                            data={'detail': 'Метод "PUT" не разрешен.'})
        return super().update(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeReadSerializer
        elif self.action == 'favorite':
            return FavoritesSerializer
        elif self.action == 'shopping_cart':
            return CartSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer: RecipeCreateSerializer):
        user = self.request.user
        serializer.is_valid(raise_exception=True)
        serializer.save(author=user)

    def __post_extra_action(self, request: Request, model, pk: int):
        """
        Добавление рецепта в список покупок/избранное.
        """
        if Recipe.objects.filter(id=pk).exists():
            user = request.user
            recipe: Recipe = Recipe.objects.get(id=pk)
            object_exists: bool = model.objects.filter(
                user=user,
                recipe=recipe
            ).exists()
            if object_exists:
                return Response(
                    {'errors': 'Выбранный рецепт уже добавлен.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user, recipe=recipe)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED)
        return Response(
            {'errors': 'Выбранный рецепт не существует.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @staticmethod
    def __delete_extra_action(request: Request, model, pk: int):
        """
        Удаление рецепта из списка покупок/избранного.
        """
        user = request.user
        recipe: Recipe = get_object_or_404(Recipe, id=pk)
        object_exists: bool = model.objects.filter(
            user=user,
            recipe=recipe
        ).exists()
        if not object_exists:
            return Response(
                data={'errors': 'Выбранный рецепт ранее не был добавлен.'},
                status=status.HTTP_400_BAD_REQUEST)
        model.objects.get(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated, ]
    )
    def favorite(self, request: Request, pk: int):
        """
        Добавить рецепт в избранное.
        """
        return self.__post_extra_action(
            request=request,
            model=FavoritRecipe,
            pk=pk
        )

    @favorite.mapping.delete
    def delete_favorite(self, request: Request, pk: int):
        """
        Удалить рецепт из избранного.
        """
        return self.__delete_extra_action(
            request=request,
            model=FavoritRecipe,
            pk=pk
        )

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated, ])
    def shopping_cart(self, request: Request, pk: int):
        """
        Добавить рецепт в список покупок.
        """
        return self.__post_extra_action(
            request=request,
            model=Cart,
            pk=pk
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request: Request, pk: int):
        """
        Удалить рецепт из списка покупок.
        """
        return self.__delete_extra_action(
            request=request,
            model=Cart,
            pk=pk
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated, ]
    )
    def download_shopping_cart(self, request: Request):
        """
        Получить список покупок в формате .txt.
        """
        user = request.user
        if user.shop_list.exists():
            shopping_list = ShoppingListCreator(
                user=user
            ).create_shopping_list()
            response = HttpResponse(shopping_list, content_type='text/plain')
            response['Content-Disposition'] = (
                f'attachment; filename={user.username}_shopping_list.txt'
            )
            return response

        return Response(
            data={'errors': 'Список покупок пуст.'},
            status=status.HTTP_400_BAD_REQUEST
        )
