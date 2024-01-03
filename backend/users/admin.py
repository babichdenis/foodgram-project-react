from django.contrib import admin
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import TokenProxy

from users.models import CustomUser, Follow


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'id', 'email', 'first_name', 'last_name')
    list_filter = ('email', 'first_name')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('author', 'user')


admin.site.unregister(Group)
admin.site.unregister(TokenProxy)
