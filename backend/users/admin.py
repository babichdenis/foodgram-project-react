from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from recipes.models import FavoriteRecipe, Cart
from .models import Subscription

User = get_user_model()

admin.site.site_header = 'Администрирование Foodgram'
admin.site.index_title = 'Администрирование сайта Foodgram'
admin.site.empty_value_display = "Не задано"


class FavoriteInline(admin.TabularInline):
    model = FavoriteRecipe
    extra = 1


class ShoppingCartInline(admin.TabularInline):
    model = Cart
    extra = 1


@admin.register(User)
class UserAdmin(UserAdmin):
    """Административная панель для управления пользователями."""

    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'date_joined'
    )
    search_fields = (
        'email',
        'username',
        'first_name',
        'last_name'
    )
    list_filter = (
        'email',
        'first_name'
    )
    inlines = (FavoriteInline, ShoppingCartInline)
    ordering = ('username', )


@admin.register(Subscription)
class SubscribeAdmin(admin.ModelAdmin):
    """Oтображение в админке модели Subscribe"""

    list_display = ('author', 'user')
