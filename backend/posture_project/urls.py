from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/posture/", include("posture.urls")),
    path("api/exercises/", include("exercises.urls")),
    path("api/subscriptions/", include("subscriptions.urls")),
]
