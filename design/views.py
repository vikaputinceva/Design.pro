from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import CustomUserCreatingForm, ApplicationForm
from .models import CustomUser, Application, Category


def index(request):
    completed_applications = Application.objects.filter(status="D").select_related('category').order_by('-date')[:4]
    in_progress = Application.objects.filter(status="P").count()



    context = {
        'completed_applications': completed_applications,
        'in_progress': in_progress,
        'is_admin': request.user.is_authenticated and request.user.is_staff,
        'is_regular_user': request.user.is_authenticated and not request.user.is_staff,
        'is_guest': not request.user.is_authenticated,
    }

    return render(request, 'index.html', context)


def logout_view(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из аккаунта.')
    return redirect('index')


class Registration(generic.CreateView):
    template_name = 'main/register.html'
    form_class = CustomUserCreatingForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        messages.success(self.request, 'Регистрация успешна! Теперь вы можете войти.')
        return super().form_valid(form)


@login_required
def create_application(request):
    if request.method == "POST":
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.applicant = request.user
            application.save()
            messages.success(request, 'Заявка успешно создана!')
            return redirect('profile')
    else:
        form = ApplicationForm()

    return render(request, 'main/application-create.html', {'form': form})


class Profile(LoginRequiredMixin, generic.View):
    template_name = 'main/profile.html'

    def get(self, request):
        status_filter = request.GET.get('status', '')

        if status_filter:
            applications = Application.objects.filter(applicant=request.user, status=status_filter).order_by(
                '-date')  # исправлено: user → applicant
        else:
            applications = Application.objects.filter(applicant=request.user).order_by(
                '-date')  # исправлено: user → applicant

        context = {
            'user': request.user,
            'applications': applications,
            'status_filter': status_filter,
            'status_choices': Application.STATUS_CHOICES,
        }

        return render(request, self.template_name, context)


class ApplicationDetailView(LoginRequiredMixin, generic.DetailView):
    model = Application
    template_name = 'main/application-detail.html'
    context_object_name = 'application'

    def get_queryset(self):
        if self.request.user.is_staff:
            return Application.objects.all()
        return Application.objects.filter(applicant=self.request.user)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Проверка прав (только для пользователя)
        if not request.user == self.object.applicant:
            messages.error(request, 'Вы не можете изменять эту заявку.')
            return self.get(request, *args, **kwargs)

        action = request.POST.get('action')

        if action == 'delete':
            if self.object.status == 'N':
                self.object.delete()
                messages.success(request, 'Заявка удалена.')
                return redirect('profile')
            else:
                messages.error(request, 'Можно удалять только новые заявки.')

        return self.get(request, *args, **kwargs)


@login_required
def delete_application(request, pk):
    application = get_object_or_404(Application, pk=pk)

    if application.applicant != request.user:
        messages.error(request, 'Вы не можете удалить эту заявку.')
        return redirect('profile')

    if application.status != 'N':
        messages.error(request, 'Можно удалять только новые заявки.')
        return redirect('profile')

    application.delete()
    messages.success(request, 'Заявка успешно удалена.')
    return redirect('profile')