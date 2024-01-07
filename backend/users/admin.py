from django.contrib import admin
from users.models import Subscription, User

EMPTY_MESSAGE = '-пусто-'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'date_joined',
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
    ordering = ('username', )
    empty_value_display = EMPTY_MESSAGE

    def count_subscribers(self, obj):
        return obj.subscriber.count()

    def count_recipes(self, obj):
        return obj.recipes.count()


@admin.register(Subscription)
class Subscription(admin.ModelAdmin):
    list_display = ('user', 'author')
    search_fields = (
        'author__username',
        'author__email',
        'user__username',
        'user__email'
    )
    list_filter = ('author__username', 'user__username')
    empty_value_display = EMPTY_MESSAGE
