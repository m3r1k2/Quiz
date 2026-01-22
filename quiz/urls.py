from django.urls import path
from .views import (
    QuizListView,
    QuizDetailView,
    QuizCreateView,
    QuizUpdateView,
    QuizDeleteView,
    QuestionCreateView,
    CreateRoomView,
    JoinRoomView,
    RoomLobbyView,
    RoomPlayView,
    quiz_result,
)

app_name = "quiz"

urlpatterns = [
    path("", QuizListView.as_view(), name="list"),
    path("create/", QuizCreateView.as_view(), name="create"),
    path("<int:pk>/", QuizDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", QuizUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", QuizDeleteView.as_view(), name="delete"),

    path("<int:quiz_id>/question/create/", QuestionCreateView.as_view(), name="question_create"),

    path("room/create/<int:pk>/", CreateRoomView.as_view(), name="room_create"),
    path("room/join/", JoinRoomView.as_view(), name="room_join"),
    path("room/<str:code>/", RoomLobbyView.as_view(), name="room_lobby"),
    path("room/<str:code>/play/", RoomPlayView.as_view(), name="room_play"),

    # 🔥 ВАЖНО
    path("room/<str:code>/result/", quiz_result, name="room_result"),
]
