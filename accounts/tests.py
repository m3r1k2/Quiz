from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from quiz.models import Quiz, Result

User = get_user_model()


class MyQuizzesViewTest(TestCase):
    def setUp(self):
        # Создаём двух пользователей
        self.user1 = User.objects.create_user(username="user1", password="pass123")
        self.user2 = User.objects.create_user(username="user2", password="pass123")


        self.quiz1 = Quiz.objects.create(
            title="Quiz A",
            complexity="easy",
            theme="math",
            que_time=20,
            que_count=5,
            author=self.user1,
        )

        # Квизы user2
        self.quiz2 = Quiz.objects.create(
            title="Quiz B",
            complexity="hard",
            theme="bio",
            que_time=30,
            que_count=10,
            author=self.user2,
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("accounts:my_quizzes"))
        self.assertEqual(response.status_code, 302)  # redirect to login

    def test_user_sees_only_own_quizzes(self):
        self.client.login(username="user1", password="pass123")
        response = self.client.get(reverse("accounts:my_quizzes"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/my_quizzes.html")

        quizzes = response.context["quizzes"]
        self.assertEqual(len(quizzes), 1)
        self.assertEqual(quizzes[0], self.quiz1)


class MyResultsViewTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="pass123")
        self.user2 = User.objects.create_user(username="user2", password="pass123")

        self.quiz = Quiz.objects.create(
            title="Quiz Test",
            complexity="medium",
            theme="science",
            que_time=15,
            que_count=7,
            author=self.user1,
        )


        self.result1 = Result.objects.create(
            quiz=self.quiz, user=self.user1, score=80
        )


        self.result2 = Result.objects.create(
            quiz=self.quiz, user=self.user2, score=40
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("accounts:my_results"))
        self.assertEqual(response.status_code, 302)

    def test_user_sees_only_their_results(self):
        self.client.login(username="user1", password="pass123")
        response = self.client.get(reverse("accounts:my_results"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/my_results.html")

        results = response.context["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], self.result1)