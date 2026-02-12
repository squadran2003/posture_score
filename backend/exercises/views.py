from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .models import Exercise, UserExerciseLog
from .recommender import recommend_exercises
from .serializers import ExerciseSerializer, UserExerciseLogSerializer


class ExerciseListView(generics.ListAPIView):
    serializer_class = ExerciseSerializer

    def get_queryset(self):
        qs = Exercise.objects.select_related("category").all()
        target = self.request.query_params.get("target_issue")
        if target:
            qs = qs.filter(target_issue=target)
        difficulty = self.request.query_params.get("difficulty")
        if difficulty:
            qs = qs.filter(difficulty=difficulty)
        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(category__name__iexact=category)
        return qs


class ExerciseDetailView(generics.RetrieveAPIView):
    serializer_class = ExerciseSerializer
    queryset = Exercise.objects.select_related("category").all()


class RecommendedExercisesView(generics.ListAPIView):
    """Returns exercises targeted at the user's weakest posture components."""

    serializer_class = ExerciseSerializer
    pagination_class = None  # Return all recommendations without pagination

    def get_queryset(self):
        limit = int(self.request.query_params.get("limit", 6))
        limit = min(limit, 12)  # Cap at 12
        return recommend_exercises(self.request.user, limit=limit)


class ExerciseLogCreateView(generics.CreateAPIView):
    """Log that the user completed an exercise."""

    serializer_class = UserExerciseLogSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ExerciseLogListView(generics.ListAPIView):
    """List the user's exercise completion history."""

    serializer_class = UserExerciseLogSerializer

    def get_queryset(self):
        return (
            UserExerciseLog.objects.filter(user=self.request.user)
            .select_related("exercise")
        )
