from django.urls import path

from . views import RegisterView,LoginView,RefreshView

app_name = "account"

urlpatterns=[
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", RefreshView.as_view(), name="refresh"),
]