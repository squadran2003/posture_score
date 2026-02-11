from rest_framework import generics, permissions

from .models import Exercise
from .serializers import ExerciseSerializer


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
        return qs


class ExerciseDetailView(generics.RetrieveAPIView):
    serializer_class = ExerciseSerializer
    queryset = Exercise.objects.select_related("category").all()


class RecommendedExercisesView(generics.ListAPIView):
    """Placeholder - full recommendation logic in Phase 4."""

    serializer_class = ExerciseSerializer

    def get_queryset(self):
        return Exercise.objects.filter(is_premium=False)[:3]
