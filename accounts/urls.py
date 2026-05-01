from django.urls import path, include
from rest_framework import routers
from .views import AuthViewSet, UsersViewsets

router = routers.DefaultRouter()
router.register(r'users', UsersViewsets, basename='users')

# Map AuthViewSet actions manually using as_view()
auth_viewset = AuthViewSet

urlpatterns = [
    # Auth endpoints (manual mapping)
    path(
        "register/normal/",
        auth_viewset.as_view({'post': 'register_normal'}),
        name="auth-register-normal",
    ),
    path(
        "register/community/",
        auth_viewset.as_view({'post': 'register_community'}),
        name="auth-register-community",
    ),
    path(
        "login/",
        auth_viewset.as_view({'post': 'login'}),
        name="auth-login",
    ),
    path(
        "logout/",
        auth_viewset.as_view({'post': 'logout'}),
        name="auth-logout",
    ),
    path(
        "profile/",
        auth_viewset.as_view({'get': 'profile'}),
        name="auth-profile",
    ),

    # User management (via router)
    path("", include(router.urls)),
]