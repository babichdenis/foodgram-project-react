from django.contrib import admin

from .models import CustomUser

admin.site.empty_value_display = "Не задано"


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    """Административная панель для управления пользователями."""

    list_display = ('id', 'username', 'email', 'first_name',
                    'last_name')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('first_name', 'last_name', 'email')
