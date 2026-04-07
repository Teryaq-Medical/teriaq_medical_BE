from django.urls import path
from .views import (
    DashboardView,
    AppointmentChartView,
    RecentAppointmentsView,
    EntitiesViewSet
)


entities_list = EntitiesViewSet.as_view({
    "get": "list",
    "post": "create",
})

entities_detail = EntitiesViewSet.as_view({
    "get": "retrieve",
    "put": "update",
})


urlpatterns = [

    path("stats/", DashboardView.as_view()),

    path("appointments-chart/", AppointmentChartView.as_view()),

    path("recent-appointments/", RecentAppointmentsView.as_view()),

    path(
        "entities/<str:entity_type>/",
        entities_list,
        name="entities-list"
    ),

    path(
        "entities/<str:entity_type>/<int:pk>/",
        entities_detail,
        name="entities-detail"
    ),
]