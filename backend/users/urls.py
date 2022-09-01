from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'users'

router = DefaultRouter()
router.register('users', views.UserViewSet, 'users')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
