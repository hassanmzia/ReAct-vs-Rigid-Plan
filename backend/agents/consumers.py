"""WebSocket consumers for real-time agent execution updates."""

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class AgentExecutionConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for streaming agent execution progress."""

    async def connect(self):
        self.session_id = self.scope["url_route"]["kwargs"]["session_id"]
        self.group_name = f"agent_{self.session_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        await self.send(text_data=json.dumps({
            "type": "connection_established",
            "session_id": self.session_id,
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg_type = data.get("type", "")

        if msg_type == "ping":
            await self.send(text_data=json.dumps({"type": "pong"}))

    async def agent_update(self, event):
        """Send agent execution update to WebSocket."""
        await self.send(text_data=json.dumps({
            "type": "agent_update",
            "data": event["data"],
        }))


class DashboardConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for dashboard real-time updates."""

    async def connect(self):
        self.group_name = "dashboard"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def dashboard_update(self, event):
        await self.send(text_data=json.dumps({
            "type": "dashboard_update",
            "data": event["data"],
        }))
