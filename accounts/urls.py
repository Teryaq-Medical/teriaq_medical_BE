from django.urls import path
from .views import (
    register_normal,
    register_community,
    login_view,
    logout_view,
    profile
)

urlpatterns = [
    path("register/normal/", register_normal),
    path("register/community/", register_community),
    path("login/", login_view),
    path("logout/", logout_view),
    path("profile/", profile),
]
