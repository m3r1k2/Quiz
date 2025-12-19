from django import forms
from .models import User

class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Підтвердження пароля", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "email", "bio", "avatar"]
        labels = {
            "username": "Ім'я користувача",
            "email": "Електронна пошта",
            "bio": "Опис",
            "avatar": "Аватар",
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Паролі не співпадають")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])  # обязательно хэшируем
        if commit:
            user.save()
        return user

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["bio", "avatar"]
        labels = {
            "bio": "Опис профілю",
            "avatar": "Фото користувача"
        }