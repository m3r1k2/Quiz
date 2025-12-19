from django.views.generic import ListView, DetailView, FormView, TemplateView, UpdateView, DeleteView, CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Quiz, Question, Answer, Result, QuizRoom, QuizPlayer
from .forms import QuizForm, QuestionForm, AnswerFormSet
from django.shortcuts import render, redirect, get_object_or_404


class QuizListView(LoginRequiredMixin, ListView):
    model = Quiz
    template_name = "quiz_list.html"
    context_object_name = "quizzes"

    def get_queryset(self):

        return Quiz.objects.all()


class QuizDetailView(LoginRequiredMixin, DetailView):
    model = Quiz
    template_name = "quiz/quiz_detail.html"
    context_object_name = "quiz"



class QuizPlayView(LoginRequiredMixin, TemplateView):
    template_name = "quiz/quiz_play.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz = Quiz.objects.get(pk=self.kwargs["pk"])
        context["quiz"] = quiz
        context["questions"] = quiz.questions.prefetch_related("answers")
        return context

    def post(self, request, *args, **kwargs):
        quiz = Quiz.objects.get(pk=self.kwargs["pk"])
        questions = quiz.questions.all()
        correct = 0

        for question in questions:
            selected_id = request.POST.get(f"question_{question.id}")
            if selected_id:
                ans = Answer.objects.get(id=selected_id)
                if ans.correct:
                    correct += 1

        Result.objects.create(user=request.user, quiz=quiz, score=correct)
        return redirect("quiz:result", pk=quiz.pk)
class QuizResultView(LoginRequiredMixin, TemplateView):
    template_name = "quiz/quiz_result.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz = Quiz.objects.get(pk=self.kwargs["pk"])
        result = Result.objects.filter(user=self.request.user, quiz=quiz).last()
        context["quiz"] = quiz
        context["result"] = result
        context["score"] = result.score if result else 0 #######
        return context


class QuizCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Quiz
    form_class = QuizForm
    template_name = "quiz/quiz_create.html"

    def test_func(self):
        user = self.request.user
        return (
            user.groups.filter(name="QuizAdmin").exists()
            or user.is_superuser
        )

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("quiz:detail", kwargs={"pk": self.object.pk})

class QuestionCreateView(View):
    template_name = "quiz/question_create.html"

    def get(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, pk=quiz_id)

        question = Question(quiz=quiz)

        question_form = QuestionForm(instance=question)
        answer_formset = AnswerFormSet(instance=question)

        return render(request, self.template_name, {
            "quiz": quiz,
            "question_form": question_form,
            "answer_formset": answer_formset,
        })

    def post(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, pk=quiz_id)

        question = Question(quiz=quiz)

        question_form = QuestionForm(request.POST, request.FILES, instance=question)
        answer_formset = AnswerFormSet(request.POST, instance=question)

        if question_form.is_valid() and answer_formset.is_valid():
            question = question_form.save()
            answer_formset.save()
            return redirect("quiz:detail", pk=quiz_id)

        return render(request, self.template_name, {
            "quiz": quiz,
            "question_form": question_form,
            "answer_formset": answer_formset,
        })


class QuizUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Quiz
    form_class = QuizForm
    template_name = "quiz/quiz_edit.html"

    def get_success_url(self):
        return reverse_lazy("quiz:detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["quiz"] = self.object
        return context

    def test_func(self):
        user = self.request.user
        quiz = self.get_object()

        return (
                user == quiz.author
                or user.groups.filter(name="QuizAdmin").exists()
                or user.is_superuser
        )
class QuizDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Quiz
    template_name = "quiz/quiz_confirm_delete.html"
    success_url = reverse_lazy("quiz:list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["quiz"] = self.object
        return context

    def test_func(self):
        user = self.request.user
        quiz = self.get_object()

        return (
                user == quiz.author
                or user.groups.filter(name="QuizAdmin").exists()
                or user.is_superuser
        )

class CreateRoomView(LoginRequiredMixin, View):
    def get(self, request, pk):
        quiz = get_object_or_404(Quiz, pk=pk)

        room = QuizRoom.objects.create(
            quiz=quiz,
            host=request.user
        )
        QuizPlayer.objects.create(room=room, user=request.user)

        return redirect("quiz:room_lobby", code=room.code)

class JoinRoomView(LoginRequiredMixin, View):
    def post(self, request):
        code = request.POST.get("code")

        room = get_object_or_404(QuizRoom, code=code)

        # якщо ще не в кімнаті
        QuizPlayer.objects.get_or_create(room=room, user=request.user)

        return redirect("quiz:room_lobby", code=code)

    def get(self, request):
        return render(request, "quiz/room_join.html")

class RoomLobbyView(LoginRequiredMixin, DetailView):
    model = QuizRoom
    slug_field = "code"
    slug_url_kwarg = "code"
    template_name = "quiz/room_lobby.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room = self.get_object()
        context["players"] = room.players.all()

        return context

class StartRoomView(LoginRequiredMixin, View):
    def get(self, request, code):
        room = get_object_or_404(QuizRoom, code=code)

        if room.host != request.user:
            return redirect("quiz:room_lobby", code=code)

        return redirect("quiz:play", pk=room.quiz.pk)

class RoomPlayView(LoginRequiredMixin, TemplateView):
    template_name = "quiz/game_play.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        room = get_object_or_404(QuizRoom, code=self.kwargs["code"])
        player = QuizPlayer.objects.get(room=room, user=self.request.user)
        ctx["room"] = room
        ctx["player"] = player
        return ctx