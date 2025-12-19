from django.urls import reverse_lazy
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, DetailView, UpdateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import RegisterForm, ProfileEditForm
from .models import User
from quiz.models import  Quiz, Result
from django.shortcuts import redirect

class RegisterView(CreateView):
    model = User
    form_class = RegisterForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("main")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect("main")

class CustomLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = AuthenticationForm

    def get_success_url(self):
        return reverse_lazy("main")


class UserLogoutView(LogoutView):
    next_page = reverse_lazy("accounts:login")


class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "accounts/profile.html"
    context_object_name = "user"

    def get_object(self, queryset=None):
        return self.request.user


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileEditForm
    template_name = "accounts/profile_edit.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self, queryset=None):
        return self.request.user



class MyQuizzesView(LoginRequiredMixin, ListView):
    model = Quiz
    template_name = "accounts/my_quizzes.html"
    context_object_name = "quizzes"

    def get_queryset(self):
        return Quiz.objects.filter(author=self.request.user)

class MyResultsView(LoginRequiredMixin,ListView):
    model = Result
    template_name = "accounts/my_results.html"
    context_object_name = "results"

    def get_queryset(self):
        return Result.objects.filter(user = self.request.user).select_related("quiz")