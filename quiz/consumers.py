import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import QuizRoom, QuizPlayer, Question


class RoomConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.code = self.scope["url_route"]["kwargs"]["code"]
        self.room_group = f"room_{self.code}"

        await self.channel_layer.group_add(self.room_group, self.channel_name)
        await self.accept()

        # Обновляем список игроков
        await self.update_players()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")

        if action == "start":
            await self.start_quiz()

        elif action == "answer":
            await self.save_answer(data)

    async def update_players(self):
        room = QuizRoom.objects.get(code=self.code)
        players = list(room.players.values("user__username"))

        await self.channel_layer.group_send(
            self.room_group,
            {
                "type": "send_to_clients",
                "payload": {
                    "event": "players",
                    "players": players,
                },
            },
        )

    async def start_quiz(self):
        await self.show_question(0)

    async def show_question(self, index):
        room = QuizRoom.objects.get(code=self.code)
        quiz = room.quiz
        questions = list(quiz.questions.all())

        # Конец викторины
        if index >= len(questions):
            await self.finish_quiz()
            return

        q = questions[index]

        await self.channel_layer.group_send(
            self.room_group,
            {
                "type": "send_to_clients",
                "payload": {
                    "event": "question",
                    "id": q.id,
                    "text": q.text,
                    "answers": [a.answer_choose for a in q.answers.all()],
                    "time": quiz.que_time,
                    "index": index,
                },
            },
        )

    async def save_answer(self, data):
        player_id = data["player_id"]
        question_id = data["question_id"]
        answer_id = data["answer_id"]

        player = QuizPlayer.objects.get(id=player_id)
        q = Question.objects.get(id=question_id)
        correct = q.answers.filter(id=answer_id, correct=True).exists()

        if correct:
            player.score += 1
            player.save()

    async def finish_quiz(self):
        room = QuizRoom.objects.get(code=self.code)
        players = list(
            room.players.order_by("-score").values("user__username", "score")
        )

        await self.channel_layer.group_send(
            self.room_group,
            {
                "type": "send_to_clients",
                "payload": {
                    "event": "finish",
                    "results": players,
                },
            },
        )

    async def send_to_clients(self, event):
        await self.send(text_data=json.dumps(event["payload"]))