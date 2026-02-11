from rest_framework import serializers

from .models import Exercise, ExerciseCategory, UserExerciseLog


class ExerciseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExerciseCategory
        fields = ["id", "name", "description"]


class ExerciseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Exercise
        fields = [
            "id",
            "name",
            "description",
            "instructions",
            "category",
            "category_name",
            "target_issue",
            "difficulty",
            "duration_seconds",
            "repetitions",
            "video_url",
            "image_url",
            "is_premium",
        ]


class UserExerciseLogSerializer(serializers.ModelSerializer):
    exercise_name = serializers.CharField(source="exercise.name", read_only=True)

    class Meta:
        model = UserExerciseLog
        fields = ["id", "exercise", "exercise_name", "completed_at"]
        read_only_fields = ["completed_at"]
