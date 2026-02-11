import json

from channels.generic.websocket import AsyncJsonWebsocketConsumer


class PostureConsumer(AsyncJsonWebsocketConsumer):
    """Placeholder WebSocket consumer - full implementation in Phase 2."""

    async def connect(self):
        self.user = self.scope.get("user")
        if not self.user or self.user.is_anonymous:
            await self.close(code=4001)
            return
        await self.accept()

    async def receive_json(self, content):
        action = content.get("action")
        if action == "start_session":
            await self.send_json({"type": "session_started"})
        elif action == "frame":
            await self.send_json({"type": "posture_result", "score": 0, "details": {}, "issues": []})
        elif action == "end_session":
            await self.send_json({"type": "session_ended"})

    async def disconnect(self, code):
        pass
