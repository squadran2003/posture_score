from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import SubscriptionPlan
from .serializers import SubscriptionPlanSerializer


class PlanListView(generics.ListAPIView):
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.AllowAny]
    queryset = SubscriptionPlan.objects.filter(is_active=True)


class CheckoutView(APIView):
    """Placeholder - Stripe checkout implementation in Phase 6."""

    def post(self, request):
        return Response(
            {"detail": "Stripe checkout not yet configured."},
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )


class WebhookView(APIView):
    """Placeholder - Stripe webhook implementation in Phase 6."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        return Response(status=status.HTTP_200_OK)
