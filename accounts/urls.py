from django.urls import path,include
from .views import (
    register_normal,
    register_community,
    login_view,
    logout_view,
    profile,
    UsersViewsets
)

from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'users', UsersViewsets,basename='users')


urlpatterns = [
    path("register/normal/", register_normal),
    path("register/community/", register_community),
    path("login/", login_view),
    path("logout/", logout_view),
    path("profile/", profile),
    path("",include(router.urls))
]
