from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path("ws/posture/analyze/", consumers.PostureConsumer.as_asgi()),
]
