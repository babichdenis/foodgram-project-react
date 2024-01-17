from django.contrib import admin

from users.models import User, Subscription

admin.site.empty_value_display = "Не задано"


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
        'count_subscribers',
        'count_recipes'
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

    def count_subscribers(self, obj):
        return obj.subscriber.count()

    def count_recipes(self, obj):
        return obj.recipes.count()


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    search_fields = (
        'author__username',
        'author__email',
        'user__username',
        'user__email'
    )
    list_filter = ('author__username', 'user__username')
