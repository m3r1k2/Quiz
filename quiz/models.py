from django.db import models
from django.conf import settings
import random
import string
class Quiz(models.Model):
    title = models.CharField(max_length=100, verbose_name="Назва вікторини")
    complexity = models.CharField(
        max_length=20,
        choices=[
            ('easy', 'Легка'),
            ('medium', 'Середня'),
            ('hard', 'Складна'),
        ],
        default='medium',
        verbose_name="Складність"
    )
    theme = models.CharField(max_length=50, verbose_name="Тема")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quizzes',
        verbose_name="Автор"
    )
    que_time = models.PositiveIntegerField(default=30, verbose_name="Час на запитання (сек)")
    que_count = models.PositiveIntegerField(default=10, verbose_name="Кількість запитань")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.invite_code:
            # генеруємо унікальний код (uuid4 короткий)
            self.invite_code = str(uuid.uuid4())[:8]
        super().save(*args, **kwargs)



    def __str__(self):
        return self.title


class Question(models.Model):
    QUESTION_TYPES = [
        ('text', 'Текст'),
        ('image', 'Зображення'),
        ('video', 'Відео'),
    ]
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=255, verbose_name="Текст запитання")
    tipe = models.CharField(max_length=10, choices=QUESTION_TYPES, default='text', verbose_name="Тип запитання")
    file = models.FileField(upload_to='questions/', blank=True, null=True, verbose_name="Файл (зображення/відео)")
    time_limit = models.PositiveIntegerField(default=15, verbose_name="Час на питання (сек)")

    def __str__(self):
        return self.text


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    answer_choose = models.CharField(max_length=255, verbose_name="Варіант відповіді")
    correct = models.BooleanField(default=False, verbose_name="Правильний")

    def __str__(self):
        return self.answer_choose


class Result(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='results'
    )
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='results')
    score = models.PositiveIntegerField(default=0, verbose_name="Бали")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} ({self.score} балів)"


def generate_room_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

class QuizRoom(models.Model):
    quiz = models.ForeignKey("Quiz", on_delete=models.CASCADE, related_name="rooms")
    host = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, unique=True, default=generate_room_code)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Room {self.code}"

class QuizPlayer(models.Model):
    room = models.ForeignKey(QuizRoom, on_delete=models.CASCADE, related_name="players")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} in {self.room.code}"