from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

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


def create_application(request):
    if request.method == "POST":
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.applicant = request.user
            application.save()
            return redirect('profile')

    else:
        form = ApplicationForm()

    return render(request, 'main/application-create.html', {'form': form})

class Profile(LoginRequiredMixin, generic.DetailView):
    model = CustomUser
    template_name = 'main/profile.html'
    context_object_name = 'user_profile'

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        status_filter = self.request.GET.get('status', '')

        if status_filter:
            application = Application.objects.filter(applicant=self.request.user, status=status_filter).order_by('date')
        else:
            application = Application.objects.filter(applicant=self.request.user).order_by('date')

        context['application'] = application
        context['status_filter'] = status_filter

        return context

@login_required
def delete_application(request, pk):
    application = get_object_or_404(Application, pk=pk)
    if application.applicant == request.user:
        if application.status == 'N':
            application.delete()
            messages.success(request, 'Заявка удалена')
        else:
            messages.error(request,'Вы не можете удалить заявки, которые имеют статус "Принято в работу" и "Выполнено"')