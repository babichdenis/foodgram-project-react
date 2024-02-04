from django.urls import include, path
from rest_framework.routers import DefaultRouter
from users.views import CustomUserViewSet
from api.views import (IngredientViewSet, RecipeViewSet,
                       TagViewSet)

router = DefaultRouter()

router.register(r'users', CustomUserViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
