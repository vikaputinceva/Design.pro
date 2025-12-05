from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [

    path('', views.index, name='index'),
    path('register/', views.Registration.as_view(), name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='main/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('profile/', views.Profile.as_view(), name='profile'),
    path('create/', views.create_application, name='application-create'),
    path('application/<int:pk>/', views.ApplicationDetailView.as_view(), name='application-detail'),
    path('application/<int:pk>/delete/', views.delete_application, name='application-delete')
]