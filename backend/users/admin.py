from django.contrib import admin

from .models import Subscribe, User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'password'
    )
    list_filter = ('username', 'email')


admin.site.register(User, UserAdmin)
admin.site.register(Subscribe)
