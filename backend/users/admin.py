from django.contrib import admin

from .models import CustomUser, Subscribe

admin.site.empty_value_display = "Не задано"


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    """Административная панель для управления пользователями."""

    list_display = ('id', 'username', 'email', 'first_name',
                    'last_name', 'recipes_count')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('first_name', 'last_name', 'email')

    @admin.display(description='Кол-во рецептов')
    def recipes_count(self, obj):
        return obj.recipes.count()

    @admin.display(description='Кол-во подписчиков')
    def subscribers_count(self, obj):
        return obj.subscribed_by.count()


@admin.register(Subscribe)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')
    list_filter = ('user', 'author')


admin.site.site_title = 'Админ-панель сайта Foodgram'
admin.site.site_header = 'Админ-панель сайта Foodgram'
