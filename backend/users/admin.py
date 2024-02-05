from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import TokenProxy

from foodgram.constants import Constants
from recipes.models import Cart, FavoritRecipe, Recipe
from users.models import FoodgramUser, Subscription

User = get_user_model()

admin.site.site_header = 'Администрирование Foodgram'
admin.site.index_title = 'Администрирование сайта Foodgram'
admin.site.empty_value_display = "Не задано"


class FavoriteInline(admin.TabularInline):
    model = FavoritRecipe
    extra = 1


class ShoppingCartInline(admin.TabularInline):
    model = Cart
    extra = 1


@admin.register(User)
class FoodgramUserAdmin(UserAdmin):
    """
    Преставление, создание, редактирование и удаление пользователей.
    """

    list_display = ('id', 'username', 'email', 'followers_count',
                    'recipes_count', 'is_active', 'is_admin', 'is_staff',
                    'is_superuser')
    list_display_links = ('username', 'id')
    date_hierarchy = 'date_joined'
    search_fields = ('username', 'email', 'id')
    list_per_page = Constants.MAX_PAGE_SIZE
    list_max_show_all = Constants.MAX_PAGE_SIZE

    @admin.display(description='Админ',
                   boolean=True)
    def is_admin(self, user: FoodgramUser):
        """Булево значение является ли пользователь администратором."""
        return user.is_active

    @admin.display(description='Персонал',
                   boolean=True)
    def is_active(self, user: FoodgramUser):
        """Булево значение является ли пользователь активным."""
        return user.is_active

    @admin.display(description='Персонал',
                   boolean=True)
    def is_staff(self, user: FoodgramUser):
        """Булево значение является ли пользователь stuff"""
        return user.is_staff

    @admin.display(description='Подписчиков')
    def followers_count(self, user: FoodgramUser):
        """Счетчик подписчиков пользователя."""
        return user.following.count()

    @admin.display(description='Рецептов')
    def recipes_count(self, user: FoodgramUser):
        """Счетчик рецептов пользователя."""
        return Recipe.objects.filter(author=user).count()


@admin.register(Subscription)
class FollowAdmin(admin.ModelAdmin):
    """
    Преставление, создание, редактирование и удаление подписок.
    """
    fields = (('user', 'following'),)
    list_display = ('id', '__str__', 'user', 'following',
                    'added_date')
    list_display_links = ('__str__', 'id')
    list_filter = ('user__username',)
    search_fields = ('user__username',)
    date_hierarchy = 'added_date'
    list_per_page = Constants.MAX_PAGE_SIZE
    list_max_show_all = Constants.MAX_PAGE_SIZE


admin.site.unregister(Group)
admin.site.unregister(TokenProxy)
