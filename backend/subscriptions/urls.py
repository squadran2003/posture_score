from django.urls import path

from . import views

urlpatterns = [
    path("plans/", views.PlanListView.as_view(), name="plan-list"),
    path("checkout/", views.CheckoutView.as_view(), name="checkout"),
    path("webhook/", views.WebhookView.as_view(), name="stripe-webhook"),
]
