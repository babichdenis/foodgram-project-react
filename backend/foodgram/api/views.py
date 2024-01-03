from api.pagination import CustomPagination
from api.permissions import IsAdminAuthorOrReadOnly
from api.serializers import (AddFavoriteSerializer, FollowListSerializer,
                             FollowSerializer, IngredientSerializer,
                             ProfileSerializer, RecipeListSerializer,
                             RecipeSerializer, TagSerializer)
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from foodgram.constants import (NOT_FOLLOW_THIS_USER,
                                RECIPE_ALREADY_IN_FAVORITE,
                                RECIPE_ALREADY_IN_SHOPPING_CART,
                                RECIPE_NOT_FOUND_FOR_ADD_FAVORITE,
                                RECIPE_NOT_FOUND_FOR_ADD_SHOPPING_CART,
                                RECIPE_NOT_FOUND_FOR_REMOVE_FAVORITE,
                                RECIPE_NOT_FOUND_FOR_REMOVE_SHOPPING_CART,
                                RECIPE_NOT_IN_FAVORITE,
                                RECIPE_NOT_IN_SHOPPING_CART)
from recipes.filters import IngredientFilter, RecipeFilter
from recipes.models import (FavoriteRecipe, Ingredient, IngredientAmount,
                            Recipe, ShoppingCart, Tag)
from rest_framework import status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.generics import ListAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from users.models import CustomUser, Follow


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_me(request):

    """Получение информации о профиле текущего пользователя."""

    user = request.user
    serializer = ProfileSerializer(user, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


class UserFollowView(APIView):

    """Функция для добавления/удаления подписок."""

    def post(self, request, user_id):
        _ = get_object_or_404(CustomUser, id=user_id)
        serializer = FollowSerializer(
            data={'user': request.user.id, 'author': user_id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        _ = get_object_or_404(CustomUser, id=user_id)
        subscription = Follow.objects.filter(
            user=request.user, author_id=user_id
        )

        if not subscription:
            return Response(
                {'errors': NOT_FOLLOW_THIS_USER},
                status=status.HTTP_400_BAD_REQUEST
            )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FollowListView(ListAPIView):

    """Получение списка подписок на пользователей."""

    serializer_class = FollowListSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return CustomUser.objects.filter(following__user=self.request.user)


class IngredientsViewSet(ReadOnlyModelViewSet):

    """Вьюсет для просмотра ингредиентов."""

    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny, )
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class TagsViewSet(ReadOnlyModelViewSet):

    """Вьюсет для просмотра Тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipeViewSet(ModelViewSet):

    """Вьюсет для работы с Рецептами."""

    queryset = Recipe.objects.select_related(
        'author'
    ).prefetch_related(
        'tags',
        'ingridient_list',
        'ingridient_list__ingredient'
    )
    pagination_class = CustomPagination
    permission_classes = (IsAdminAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeListSerializer
        return RecipeSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        user = request.user

        try:
            recipe = Recipe.objects.get(id=pk)
        except Recipe.DoesNotExist:
            if request.method == 'POST':
                return Response(
                    {'detail': RECIPE_NOT_FOUND_FOR_ADD_FAVORITE},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif request.method == 'DELETE':
                return Response(
                    {'detail': RECIPE_NOT_FOUND_FOR_REMOVE_FAVORITE},
                    status=status.HTTP_404_NOT_FOUND
                )

        if request.method == 'POST':
            if FavoriteRecipe.objects.filter(
                user=user, recipe=recipe
            ).exists():
                return Response(
                    {'detail': RECIPE_ALREADY_IN_FAVORITE},
                    status=status.HTTP_400_BAD_REQUEST
                )
            FavoriteRecipe.objects.create(user=user, recipe=recipe)
            serializer = AddFavoriteSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            try:
                favorite = FavoriteRecipe.objects.get(user=user, recipe=recipe)
                favorite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except FavoriteRecipe.DoesNotExist:
                return Response(
                    {'detail': RECIPE_NOT_IN_FAVORITE},
                    status=status.HTTP_400_BAD_REQUEST
                )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        user = request.user

        try:
            recipe = Recipe.objects.get(id=pk)
        except Recipe.DoesNotExist:
            if request.method == 'POST':
                return Response(
                    {'detail': RECIPE_NOT_FOUND_FOR_ADD_SHOPPING_CART},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif request.method == 'DELETE':
                return Response(
                    {'detail': RECIPE_NOT_FOUND_FOR_REMOVE_SHOPPING_CART},
                    status=status.HTTP_404_NOT_FOUND
                )

        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'detail': RECIPE_ALREADY_IN_SHOPPING_CART},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = AddFavoriteSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            try:
                shopping_cart = ShoppingCart.objects.get(
                    user=user, recipe=recipe
                )
                shopping_cart.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except ObjectDoesNotExist:
                return Response(
                    {'detail': RECIPE_NOT_IN_SHOPPING_CART},
                    status=status.HTTP_400_BAD_REQUEST
                )

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        user = request.user

        ingredients = IngredientAmount.objects.filter(
            recipe__shopping_recipe__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))

        user_full_name = user.get_full_name()
        shopping_list = (
            f'Список покупок для: {user_full_name}\n\n'
            f'Foodgram\n\n'
        )
        shopping_list += '\n'.join([
            f'- {ingredient["ingredient__name"]} '
            f'({ingredient["ingredient__measurement_unit"]})'
            f' - {ingredient["amount"]}'
            for ingredient in ingredients
        ])

        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; \
        filename="shopping_list.txt"'

        return response


class UserViewSet(UserViewSet):

    """Вьюсет для пользователя."""

    serializer_class = ProfileSerializer
    pagination_class = LimitOffsetPagination
