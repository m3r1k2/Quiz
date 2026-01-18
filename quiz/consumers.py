import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import QuizRoom, Answer, QuizPlayer


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

        # ✅ ПРИЁМ МНОЖЕСТВЕННОГО ОТВЕТА
        if data.get("action") == "answer":
            await self.check_answer(data)

    @database_sync_to_async
    def check_answer(self, data):
        player = QuizPlayer.objects.get(
            id=data["player_id"]
        )

        user_answers = set(data.get("answers", []))

        correct_answers = set(
            Answer.objects.filter(
                question_id=data["question_id"],
                correct=True
            ).values_list("id", flat=True)
        )

        if user_answers == correct_answers:
            player.score += 1
            player.save()

    async def send_event(self, event):
        await self.send(text_data=json.dumps(event["data"]))