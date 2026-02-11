from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    TIER_CHOICES = [
        ("free", "Free"),
        ("pro", "Pro"),
        ("premium", "Premium"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    tier = models.CharField(max_length=10, choices=TIER_CHOICES, default="free")
    daily_sessions_used = models.PositiveIntegerField(default=0)
    daily_sessions_reset_at = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.tier})"

    @property
    def session_limit(self):
        if self.tier == "free":
            return 2
        return None  # unlimited

    @property
    def max_session_duration(self):
        """Max session duration in seconds."""
        if self.tier == "free":
            return 300  # 5 minutes
        return None  # unlimited

    @property
    def history_days(self):
        if self.tier == "free":
            return 7
        if self.tier == "pro":
            return 90
        return None  # unlimited
