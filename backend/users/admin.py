from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from recipes.models import FavoritRecipe, Cart, Recipe
from users.models import Subscription, User
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import TokenProxy

# User = get_user_model()

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
class UserAdmin(UserAdmin):
    """Административная панель для управления пользователями."""

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {'fields': ('first_name',
                                                'last_name',
                                                'email')}),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
    )
    list_display = ('id', 'username', 'email', 'followers_count',
                    'recipes_count', 'is_admin', 'is_staff',
                    'is_superuser')
    list_display_links = ('username', 'id')
    date_hierarchy = 'date_joined'
    search_fields = ('username', 'email', 'id')
    list_per_page = 50
    list_max_show_all = 100

    @admin.display(description='Статус администратора',
                   boolean=True)
    def is_admin(self, user: User):
        """Булево значение является ли пользователь администратором."""
        return user.role == 'admin'

    @admin.display(description='Подписчиков')
    def followers_count(self, user: User):
        """Счетчик подписчиков пользователя."""
        return user.following.count()

    @admin.display(description='Рецептов')
    def recipes_count(self, user: User):
        """Счетчик рецептов пользователя."""
        return Recipe.objects.filter(author=user).count()

    def save_model(self, request, obj: User, form, change):
        """
        Создание пользователя.
        Метод переопределен для автоматической
        установки статуса персонала,
        если роль пользователя - администратор.
        """
        if obj.is_admin():
            obj.is_staff = True
        else:
            obj.is_staff = False
        super().save_model(request, obj, form, change)

    inlines = (FavoriteInline, ShoppingCartInline)
    ordering = ('username', )


@admin.register(Subscription)
class FollowAdmin(admin.ModelAdmin):
    """Преставление, создание, редактирование и удаление подписок."""
    fields = (('user', 'following'),)
    list_display = ('id', '__str__', 'user', 'following',
                    'added_date')
    list_display_links = ('__str__', 'id')
    list_filter = ('user__username',)
    search_fields = ('user__username',)
    date_hierarchy = 'added_date'
    list_per_page = 50
    list_max_show_all = 100


admin.site.unregister(Group)
admin.site.unregister(TokenProxy)
