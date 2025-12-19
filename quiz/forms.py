from django import forms
from .models import Quiz, Question, Answer
from django.forms import inlineformset_factory

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'complexity', 'theme', 'que_time', 'que_count']
        labels = {
            'title': 'Назва вікторини',
            'complexity': 'Складність',
            'theme': 'Тема',
            'que_time': 'Час на запитання (сек)',
            'que_count': 'Кількість запитань',
        }
        help_texts = {
            'que_time': 'Скільки секунд буде на кожне запитання.',
            'que_count': 'Скільки запитань в вікторині за замовчуванням.',
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'tipe', 'file', "time_limit"]
        labels = {
            'text': 'Текст питання',
            'tipe': 'Тип запитання',
            'file': 'Файл (зображення або відео)',
        }
        help_texts = {
            'file': 'Опціонально: додайте зображення або відео для питання.',
        }

    def clean(self):
        cleaned = super().clean()
        tipe = cleaned.get('tipe')
        file = cleaned.get('file')
        if tipe in ('image', 'video') and not file:
            raise forms.ValidationError('Для типу "image" або "video" обов\'язково додати файл.')
        return cleaned

# Formset для відповідей (дочерних об'єктів Question)
AnswerFormSet = inlineformset_factory(
    parent_model=Question,
    model=Answer,
    fields=['answer_choose', 'correct'],
    extra=4,
    can_delete=True
)