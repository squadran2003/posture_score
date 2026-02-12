from django.db.models import Avg
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PostureSession
from .serializers import PostureSessionDetailSerializer, PostureSessionListSerializer


class SessionListView(generics.ListAPIView):
    serializer_class = PostureSessionListSerializer

    def get_queryset(self):
        return PostureSession.objects.filter(
            user=self.request.user,
            is_active=False,
        )


class SessionDetailView(generics.RetrieveAPIView):
    serializer_class = PostureSessionDetailSerializer

    def get_queryset(self):
        return PostureSession.objects.filter(user=self.request.user)


class StatsView(APIView):
    def get(self, request):
        days = int(request.query_params.get("days", 7))
        since = timezone.now() - timezone.timedelta(days=days)

        sessions = PostureSession.objects.filter(
            user=request.user,
            is_active=False,
            started_at__gte=since,
        )

        stats = sessions.aggregate(avg_score=Avg("average_score"))
        daily_scores = (
            sessions.annotate(day=TruncDate("started_at"))
            .values("day")
            .annotate(avg=Avg("average_score"))
            .order_by("day")
        )

        return Response(
            {
                "period_days": days,
                "total_sessions": sessions.count(),
                "average_score": stats["avg_score"],
                "daily_scores": list(daily_scores),
            }
        )
