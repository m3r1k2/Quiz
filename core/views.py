from django.shortcuts import render
from django.db.models import Count
from quiz.models import Quiz

def HomeView(request):
    popular_quizzes = (
        Quiz.objects
        .annotate(players_count=Count("rooms__players"))
        .order_by("-players_count")[:6]
    )

    latest_quizzes = Quiz.objects.order_by("-created_at")[:6]

    return render(request, "home.html", {
        "popular_quizzes": popular_quizzes,
        "latest_quizzes": latest_quizzes,
    })