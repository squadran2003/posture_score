from django.urls import path

from . import views

urlpatterns = [
    path("", views.ExerciseListView.as_view(), name="exercise-list"),
    path("recommended/", views.RecommendedExercisesView.as_view(), name="exercise-recommended"),
    path("log/", views.ExerciseLogCreateView.as_view(), name="exercise-log-create"),
    path("log/history/", views.ExerciseLogListView.as_view(), name="exercise-log-list"),
    path("<int:pk>/", views.ExerciseDetailView.as_view(), name="exercise-detail"),
]
