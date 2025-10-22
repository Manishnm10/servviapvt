from . import views
"""django_core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
"""

from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    path("", views.home, name="home"),
    path('api/register/', views.register_view, name='register'),
]
