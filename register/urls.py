from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path("", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("users_view/", views.users_view, name="users_view"),

    path("admin_view/", views.admin_view, name="admin_view"),
    path("admin_add/", views.admin_add, name="admin_add"),
    path("admin_delete/<uuid:user>", views.admin_delete, name="admin_delete"),
]
