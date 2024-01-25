from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import User

admin.site.site_header = 'Администрирование Foodgram'
admin.site.index_title = 'Администрирование сайта Foodgram'
admin.site.empty_value_display = "Не задано"


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
    ordering = ('username', )
