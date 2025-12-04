from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.views import generic
from django.urls import reverse_lazy

from .forms import CustomUserCreatingForm, ApplicationForm
from .models import CustomUser, Application

def index(request):
    return render(
        request,
        'index.html'
    )


def logout_view(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из аккаунта.')
    return redirect('login')


class Registration(generic.CreateView):
    template_name = 'main/register.html'
    form_class = CustomUserCreatingForm
    success_url = reverse_lazy('login')


def profile_view(request):
    return render(request, 'main/profile.html')
def create_application(request):
    if request.method == "POST":
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.save()
            return redirect('profile')

    else:
        form = ApplicationForm()

    return render(request, 'main/create-application.html', {'form': form})

def detail_application(request, pk):
    application = get_object_or_404(Application, pk=pk)
    return render(request, 'main/application-detail.html', {'application': application})