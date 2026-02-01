from django.urls import path
from .views import (
    register_normal_user,
    register_community_user,
    login,
    logout
)

urlpatterns = [
    path('register/normal/', register_normal_user, name='register_normal_user'),
    path('register/community/', register_community_user, name='register_community_user'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),

]
