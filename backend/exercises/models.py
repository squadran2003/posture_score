from django.conf import settings
from django.db import models


class ExerciseCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "exercise categories"

    def __str__(self):
        return self.name


class Exercise(models.Model):
    DIFFICULTY_CHOICES = [
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
    ]

    TARGET_ISSUE_CHOICES = [
        ("forward_head", "Forward Head Position"),
        ("shoulder_level", "Shoulder Levelness"),
        ("shoulder_round", "Shoulder Rounding"),
        ("spine_align", "Spine Alignment"),
        ("general", "General Posture"),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    instructions = models.TextField()
    category = models.ForeignKey(
        ExerciseCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name="exercises",
    )
    target_issue = models.CharField(max_length=20, choices=TARGET_ISSUE_CHOICES)
    difficulty = models.CharField(max_length=15, choices=DIFFICULTY_CHOICES, default="beginner")
    duration_seconds = models.PositiveIntegerField(help_text="Recommended duration in seconds")
    repetitions = models.PositiveIntegerField(null=True, blank=True)
    video_url = models.URLField(blank=True)
    image_url = models.URLField(blank=True)
    is_premium = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class UserExerciseLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="exercise_logs",
    )
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
        related_name="logs",
    )
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-completed_at"]

    def __str__(self):
        return f"{self.user.username} - {self.exercise.name}"
