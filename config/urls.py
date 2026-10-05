"""
PROJECT LEVEL URLS
"""
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/for/auth/", include("apps.accounts.api.urls")),
]
