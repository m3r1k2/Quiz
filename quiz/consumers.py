import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import QuizRoom


class RoomConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.code = self.scope["url_route"]["kwargs"]["code"]
        self.room_group = f"room_{self.code}"

        await self.channel_layer.group_add(
            self.room_group,
            self.channel_name
        )
        await self.accept()
        await self.send_players()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group,
            self.channel_name
        )

    @database_sync_to_async
    def get_players(self):
        room = QuizRoom.objects.get(code=self.code)
        return list(room.players.values_list("user__username", flat=True))

    async def send_players(self):
        players = await self.get_players()
        await self.channel_layer.group_send(
            self.room_group,
            {
                "type": "send_event",
                "data": {
                    "event": "players",
                    "players": players
                }
            }
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        print("START RECEIVED FROM", self.scope["user"])

        if data.get("action") == "start":
            await self.channel_layer.group_send(
                self.room_group,
                {
                    "type": "send_event",
                    "data": {
                        "event": "start",
                        "url": f"/quiz/room/{self.code}/play/"
                    }
                }
            )

    async def send_event(self, event):
        await self.send(text_data=json.dumps(event["data"]))