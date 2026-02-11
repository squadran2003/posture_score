from django.urls import path

from . import views

urlpatterns = [
    path("sessions/", views.SessionListView.as_view(), name="session-list"),
    path("sessions/<int:pk>/", views.SessionDetailView.as_view(), name="session-detail"),
    path("stats/", views.StatsView.as_view(), name="posture-stats"),
]
