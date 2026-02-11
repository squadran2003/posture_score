from django.urls import path

from . import views

urlpatterns = [
    path("", views.ExerciseListView.as_view(), name="exercise-list"),
    path("<int:pk>/", views.ExerciseDetailView.as_view(), name="exercise-detail"),
    path("recommended/", views.RecommendedExercisesView.as_view(), name="exercise-recommended"),
]
