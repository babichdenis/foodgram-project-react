from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.description),
    path('auth/', include('django.contrib.auth.urls')),
#    path("", include("djoser.urls")),
#    path("auth/", include("djoser.urls.authtoken")),
]
