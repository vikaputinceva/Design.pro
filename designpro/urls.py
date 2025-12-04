from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('superadmin/', admin.site.urls),
]