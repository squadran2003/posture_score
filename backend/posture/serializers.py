from rest_framework import serializers

from .models import PostureScore, PostureSession


class PostureScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostureScore
        fields = [
            "id",
            "timestamp",
            "overall_score",
            "head_position_score",
            "shoulder_levelness_score",
            "shoulder_rounding_score",
            "spine_alignment_score",
            "issues",
        ]


class PostureSessionListSerializer(serializers.ModelSerializer):
    score_count = serializers.IntegerField(source="scores.count", read_only=True)

    class Meta:
        model = PostureSession
        fields = [
            "id",
            "started_at",
            "ended_at",
            "average_score",
            "is_active",
            "score_count",
        ]


class PostureSessionDetailSerializer(serializers.ModelSerializer):
    scores = PostureScoreSerializer(many=True, read_only=True)

    class Meta:
        model = PostureSession
        fields = [
            "id",
            "started_at",
            "ended_at",
            "average_score",
            "calibration_data",
            "is_active",
            "scores",
        ]
