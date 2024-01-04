from rest_framework.routers import DefaultRouter

from django.urls import include, path

from api.views import UserViewSet

app_name = 'users'

router = DefaultRouter()

router.register('users', UserViewSet)
urlpatterns = [
    path('', include('djoser.urls')),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
