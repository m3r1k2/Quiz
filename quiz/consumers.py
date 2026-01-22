import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import QuizRoom, QuizPlayer, Answer


class RoomConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.code = self.scope["url_route"]["kwargs"]["code"]
        self.room_group = f"room_{self.code}"

        await self.channel_layer.group_add(self.room_group, self.channel_name)
        await self.accept()

        query = self.scope.get("query_string", b"").decode()
        self.is_play = "play=1" in query

        self.user = self.scope.get("user")
        self.user_id = getattr(self.user, "id", None)
        self.is_host = await self.check_is_host()

        self.timer_task = None

        # LOBBY
        if not self.is_play:
            await self.send_players()
            return

        # GAME — стартует ТОЛЬКО у хоста
        if self.is_play and self.is_host:
            await self.start_question()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group, self.channel_name)

    # ================= DB =================

    @database_sync_to_async
    def check_is_host(self):
        try:
            room = QuizRoom.objects.get(code=self.code)
            return room.host_id == self.user_id
        except QuizRoom.DoesNotExist:
            return False

    @database_sync_to_async
    def get_players(self):
        room = QuizRoom.objects.get(code=self.code)
        return list(room.players.values_list("user__username", flat=True))

    @database_sync_to_async
    def reset_answers(self):
        room = QuizRoom.objects.get(code=self.code)
        room.players.update(answered_current=False)
        room.question_active = True
        room.save()

    @database_sync_to_async
    def mark_answered(self, player_id):
        QuizPlayer.objects.filter(id=player_id).update(answered_current=True)

    @database_sync_to_async
    def all_answered(self):
        room = QuizRoom.objects.get(code=self.code)
        return not room.players.filter(answered_current=False).exists()

    @database_sync_to_async
    def get_question(self):
        room = QuizRoom.objects.get(code=self.code)
        questions = list(room.quiz.questions.prefetch_related("answers"))

        idx = room.current_question_index
        if idx >= len(questions):
            return None

        q = questions[idx]
        return {
            "event": "question",
            "id": q.id,
            "text": q.text,
            "time": q.time_limit,
            "answers": [
                {"id": a.id, "text": a.answer_choose}
                for a in q.answers.all()
            ],
        }

    @database_sync_to_async
    def next_index(self):
        room = QuizRoom.objects.get(code=self.code)
        room.current_question_index += 1
        room.question_active = False
        room.save()

    # ================= LOBBY =================

    async def send_players(self):
        players = await self.get_players()
        await self.channel_layer.group_send(
            self.room_group,
            {"type": "send_event", "data": {"event": "players", "players": players}},
        )

    # ================= GAME =================

    async def start_question(self):
        payload = await self.get_question()
        if not payload:
            await self.finish_game()
            return

        await self.reset_answers()

        await self.channel_layer.group_send(
            self.room_group,
            {"type": "send_event", "data": payload},
        )

        if self.timer_task:
            self.timer_task.cancel()

        self.timer_task = asyncio.create_task(
            self.question_timer(payload["time"])
        )

    async def question_timer(self, seconds):
        try:
            await asyncio.sleep(seconds)
            if await self.check_is_host():
                await self.force_next_question()
        except asyncio.CancelledError:
            pass

    async def force_next_question(self):
        if self.timer_task:
            self.timer_task.cancel()
            self.timer_task = None

        await self.next_index()
        await self.start_question()

    # ================= RECEIVE =================

    async def receive(self, text_data):
        data = json.loads(text_data)

        # START GAME
        if data.get("action") == "start" and not self.is_play:
            if not await self.check_is_host():
                return

            await self.channel_layer.group_send(
                self.room_group,
                {
                    "type": "send_event",
                    "data": {
                        "event": "start",
                        "url": f"/quiz/room/{self.code}/play/",
                    },
                },
            )
            return

        # ANSWER (МОГУТ ВСЕ)
        if data.get("action") == "answer" and self.is_play:
            await self.process_answer(data)

    # ================= ANSWERS =================

    @database_sync_to_async
    def check_answer(self, question_id, answers, player_id):
        correct = set(
            Answer.objects.filter(
                question_id=question_id, correct=True
            ).values_list("id", flat=True)
        )

        if set(answers) == correct:
            player = QuizPlayer.objects.get(id=player_id)
            player.score += 1
            player.save()

    async def process_answer(self, data):
        await self.check_answer(
            data["question_id"],
            data.get("answers", []),
            data["player_id"],
        )

        await self.mark_answered(data["player_id"])

        if await self.all_answered() and self.is_host:
            await self.force_next_question()

    # ================= FINISH =================

    @database_sync_to_async
    def get_results(self):
        room = QuizRoom.objects.get(code=self.code)
        return list(room.players.values("user__username", "score"))

    async def finish_game(self):
        results = await self.get_results()
        await self.channel_layer.group_send(
            self.room_group,
            {"type": "send_event", "data": {"event": "finish", "results": results}},
        )

    async def send_event(self, event):
        await self.send(text_data=json.dumps(event["data"]))