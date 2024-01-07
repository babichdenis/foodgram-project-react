from django.contrib import admin
from users.models import User

EMPTY_MESSAGE = '-пусто-'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Административная панель для управления пользователями."""

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
