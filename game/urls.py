from django.urls import path
from .views import (
    GridCreateView,
    HiddenGridDetailView,
    VisibleGridDetailView,
    GridDeleteView,
    grid_regenerate,
)

app_name = "game"

urlpatterns = [
    path("", GridCreateView.as_view(), name="grid-form"),
    path("<uuid:pk>/", HiddenGridDetailView.as_view(), name="grid-detail-hidden"),
    path(
        "<uuid:pk>/visible", VisibleGridDetailView.as_view(), name="grid-detail-visible"
    ),
    path("<uuid:pk>/delete", GridDeleteView.as_view(), name="grid-delete"),
    path("<uuid:pk>/regenerate-grid", grid_regenerate, name="grid-regenerate"),
]
