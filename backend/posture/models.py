from django.conf import settings
from django.db import models


class PostureSession(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posture_sessions",
    )
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    average_score = models.FloatField(null=True, blank=True)
    calibration_data = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"Session {self.id} - {self.user.username} ({self.started_at:%Y-%m-%d %H:%M})"


class PostureScore(models.Model):
    session = models.ForeignKey(
        PostureSession,
        on_delete=models.CASCADE,
        related_name="scores",
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    overall_score = models.FloatField()
    head_position_score = models.FloatField()
    shoulder_levelness_score = models.FloatField()
    shoulder_rounding_score = models.FloatField()
    spine_alignment_score = models.FloatField()
    issues = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"Score {self.overall_score:.1f} @ {self.timestamp:%H:%M:%S}"
