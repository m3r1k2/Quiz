from django.views.generic import (
    ListView, DetailView, UpdateView, DeleteView,
    CreateView, TemplateView, View
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Max

from .models import Quiz, Question, QuizRoom, QuizPlayer
from .forms import QuizForm, QuestionForm, AnswerFormSet


# =========================
# СПИСОК ВИКТОРИН
# =========================
class QuizListView(LoginRequiredMixin, ListView):
    model = Quiz
    template_name = "quiz/quiz_list.html"
    context_object_name = "quizzes"


# =========================
# ДЕТАЛИ ВИКТОРИНЫ
# =========================
class QuizDetailView(LoginRequiredMixin, DetailView):
    model = Quiz
    template_name = "quiz/quiz_detail.html"
    context_object_name = "quiz"


# =========================
# СОЗДАНИЕ ВИКТОРИНЫ
# =========================
class QuizCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Quiz
    form_class = QuizForm
    template_name = "quiz/quiz_create.html"

    def test_func(self):
        return self.request.user.is_superuser

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("quiz:detail", kwargs={"pk": self.object.pk})


# =========================
# РЕДАКТИРОВАНИЕ
# =========================
class QuizUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Quiz
    form_class = QuizForm
    template_name = "quiz/quiz_edit.html"

    def test_func(self):
        quiz = self.get_object()
        return self.request.user == quiz.author or self.request.user.is_superuser

    def get_success_url(self):
        return reverse_lazy("quiz:detail", kwargs={"pk": self.object.pk})


# =========================
# УДАЛЕНИЕ
# =========================
class QuizDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Quiz
    template_name = "quiz/quiz_confirm_delete.html"
    success_url = reverse_lazy("quiz:list")

    def test_func(self):
        quiz = self.get_object()
        return self.request.user == quiz.author or self.request.user.is_superuser


# =========================
# ВОПРОСЫ
# =========================
class QuestionCreateView(View):
    template_name = "quiz/question_create.html"

    def get(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        question = Question(quiz=quiz)
        return render(request, self.template_name, {
            "quiz": quiz,
            "question_form": QuestionForm(instance=question),
            "answer_formset": AnswerFormSet(instance=question),
        })

    def post(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        question = Question(quiz=quiz)
        question_form = QuestionForm(request.POST, instance=question)
        answer_formset = AnswerFormSet(request.POST, instance=question)

        if question_form.is_valid() and answer_formset.is_valid():
            question_form.save()
            answer_formset.save()
            return redirect("quiz:detail", pk=quiz_id)

        return render(request, self.template_name, {
            "quiz": quiz,
            "question_form": question_form,
            "answer_formset": answer_formset,
        })


# =========================
# КОМНАТЫ
# =========================
class CreateRoomView(LoginRequiredMixin, View):
    def get(self, request, pk):
        quiz = get_object_or_404(Quiz, pk=pk)
        room = QuizRoom.objects.create(quiz=quiz, host=request.user)
        QuizPlayer.objects.create(room=room, user=request.user)
        return redirect("quiz:room_lobby", code=room.code)


class JoinRoomView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "quiz/room_join.html")

    def post(self, request):
        code = request.POST.get("code")
        room = get_object_or_404(QuizRoom, code=code)
        QuizPlayer.objects.get_or_create(room=room, user=request.user)
        return redirect("quiz:room_lobby", code=code)


class RoomLobbyView(LoginRequiredMixin, DetailView):
    model = QuizRoom
    slug_field = "code"
    slug_url_kwarg = "code"
    template_name = "quiz/room_lobby.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["players"] = self.object.players.select_related("user")
        return context


# =========================
# ИГРА
# =========================
class RoomPlayView(LoginRequiredMixin, TemplateView):
    template_name = "quiz/game_play.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room = get_object_or_404(QuizRoom, code=self.kwargs["code"])
        player = get_object_or_404(QuizPlayer, room=room, user=self.request.user)
        context["room"] = room
        context["player"] = player
        context["quiz"] = room.quiz
        return context


# =========================
# РЕЗУЛЬТАТ КОМНАТЫ
# =========================
def quiz_result(request, code):
    room = get_object_or_404(QuizRoom, code=code)
    players = QuizPlayer.objects.filter(room=room)

    my_player = players.filter(user=request.user).first()
    top_score = players.aggregate(Max("score"))["score__max"]

    winner = None
    if top_score is not None:
        winner = players.filter(score=top_score).select_related("user").first()

    return render(
        request,
        "quiz/quiz_result.html",
        {
            "quiz": room.quiz,
            "room": room,
            "score": my_player.score if my_player else 0,
            "winner": winner,
            "is_winner": winner is not None and winner.user == request.user,
        },
    )