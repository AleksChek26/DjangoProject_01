from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import User


def register(request):
    """Страница регистрации."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Вы успешно зарегистрированы!')
            return redirect('accounts:profile')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """Страница входа."""
    # Стандартная форма аутентификации Django
    pass  # Реализуется через django.contrib.auth.views


@login_required
def profile(request):
    """Профиль пользователя."""
    return render(request, 'accounts/profile.html', {'user': request.user})


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля."""
    model = User
    form_class = CustomUserChangeForm
    template_name = 'accounts/profile_update.html'

    context_object_name = 'user'


    def get_object(self, queryset=None):
        return self.request.user


    def get_success_url(self):
        messages.success(self.request, 'Профиль обновлён.')
        return reverse('accounts:profile')
