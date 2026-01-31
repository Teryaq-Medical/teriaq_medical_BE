from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('clincs.urls')),
    path('api/', include('doctors.urls')),
    path('api/', include('hospitals.urls')),
    path('api/', include('labs.urls')),
]
