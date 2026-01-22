from django.shortcuts import render
from django.db.models import Count
from quiz.models import Quiz

def home(request):
    popular_quizzes = (
        Quiz.objects
        .annotate(play_count=Count("results"))  # 👈 ВОТ ТУТ
        .filter(play_count__gte=5)
        .order_by("-play_count")[:6]
    )

    latest_quizzes = Quiz.objects.order_by("-created_at")[:6]

    return render(request, "home.html", {
        "popular_quizzes": popular_quizzes,
        "latest_quizzes": latest_quizzes,
    })
