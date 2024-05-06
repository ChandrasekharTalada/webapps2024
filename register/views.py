from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from register.models import User
from django.contrib.auth import views as auth_views
from django.views import View
from .forms import RegistrationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("home")
        return render(request, "registration/login.html")

    def post(self, request):
        email = request.POST.get("email")
        password = request.POST.get("password")
        if email and password:
            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                messages.success(request, "Login Successful")
                return redirect("home")
            else:
                messages.error(request, "Username or password don't match")
        return render(request, "registration/login.html")


class RegisterView(View):
    def get(self, request, *args, **kwargs):
        registration_form = RegistrationForm()
        context = {
            "registration_form": registration_form,
        }
        return render(request, "registration/register.html", context)

    def post(self, request, *args, **kwargs):
        register_form = RegistrationForm(request.POST)
        if register_form.is_valid():
            register_form.save()
            messages.success(request, "User registered successfully")
            return redirect("login")
        else:
             for field, errors in register_form.errors.items():
                    for error in errors:
                        messages.warning(request, f"{field}: {error}")
        context = {
            "registration_form":RegistrationForm(),
        }
        return render(request, "registration/register.html", context)
    
@login_required
def users_view(request):
    if request.user.is_superuser:
        users = User.objects.filter(is_superuser=False)
    else:
        messages.warning(request, "User not authorized to view users")
    return render(request, "registration/users_view.html", {"users": users})


@login_required
def admin_view(request):
    if request.user.is_superuser:
        admins = User.objects.filter(is_superuser=True)
    else:
        messages.warning(request, "User not authorized to view admins")
    return render(request, "registration/admin_view.html", {"admins": admins})


@login_required
def admin_add(request):
    form = RegistrationForm()
    if request.user.is_superuser:
        if request.method == "POST":
            form = RegistrationForm(request.POST)
            if form.is_valid():
                form = form.save(commit=False)
                form.is_superuser = True
                form.save()
                messages.success(request, "Admin added successfully")
                return redirect("home")
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.warning(request, f"{field}: {error}")
    else:
        messages.warning(request, "User not authorized")
    return render(request, "registration/admin_add.html", {"form": form})


@login_required
def admin_delete(request, user):
    if request.user.is_superuser:
        admin =User.objects.filter(uuid=user).first()
        if admin:
            admin.delete()
            messages.success(request, "User deleted successfully")
            return redirect("admin_view")
    else:
        messages.warning(request, "User not authorized")
    return render(request, "registration/admin_view.html")


class LogoutView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return redirect("login")
