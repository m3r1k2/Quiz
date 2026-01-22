from django.urls import path
from .views import (
 QuizListView, QuizDetailView, QuizResultView,
 QuizUpdateView, QuizDeleteView, QuizCreateView,
 QuestionCreateView, CreateRoomView, JoinRoomView,
 RoomLobbyView, RoomPlayView
)
from django.conf import settings
from django.conf.urls.static import static

app_name = "quiz"

urlpatterns = [
    path("", QuizListView.as_view(), name="list"),
    path("<int:pk>/", QuizDetailView.as_view(), name="detail"),

    path("<int:pk>/result/", QuizResultView.as_view(), name="result"),
        path("<int:pk>/edit/", QuizUpdateView.as_view(), name="edit"),
path("<int:pk>/delete/", QuizDeleteView.as_view(), name="delete"),
            path('create/', QuizCreateView.as_view(), name='create'),
    path("<int:quiz_id>/question/create/", QuestionCreateView.as_view(), name="question_create"),
path("<int:quiz_id>/question/add/", QuestionCreateView.as_view(), name="question_add"),
path("room/create/<int:pk>/", CreateRoomView.as_view(), name="room_create"),
path("room/join/", JoinRoomView.as_view(), name="room_join"),
path("room/<str:code>/", RoomLobbyView.as_view(), name="room_lobby"),

path("room/<str:code>/play/", RoomPlayView.as_view(), name="room_play")

]
