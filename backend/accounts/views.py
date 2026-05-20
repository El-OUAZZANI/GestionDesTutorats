from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect


def redirect_authenticated_user(user):
    profile = getattr(user, "profile", None)
    if profile and profile.is_platform_admin:
        return redirect("admin_dashboard")

    return redirect("student_dashboard")


def login_view(request):
    if request.method == "GET" and request.user.is_authenticated:
        logout(request)
        messages.info(request, "Vous avez été déconnecté pour changer de compte.")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)

        if user is not None:
            profile = getattr(user, "profile", None)

            if user.is_staff or user.is_superuser or (profile and profile.is_platform_admin):
                messages.error(
                    request,
                    "Ce compte administrateur ne peut pas se connecter ici. Utilisez l'espace admin.",
                )
                return render(request, "accounts/login.html")

            login(request, user)
            return redirect_authenticated_user(user)
        else:
            messages.error(request, "Email ou mot de passe incorrect.")

    return render(request, "accounts/login.html")


def admin_login_view(request):
    if request.method == "GET" and request.user.is_authenticated:
        logout(request)
        messages.info(request, "Vous avez été déconnecté pour changer de compte.")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)

        if user is not None:
            profile = getattr(user, "profile", None)

            if user.is_staff or user.is_superuser:
                messages.error(
                    request,
                    "Ce compte est réservé à Django admin. Utilisez /django-admin/.",
                )
                return render(request, "accounts/admin_login.html")

            if profile and profile.is_platform_admin:
                login(request, user)
                return redirect("admin_dashboard")

            messages.error(request, "Ce compte n'a pas l'autorisation d'accéder à l'espace admin.")
        else:
            messages.error(request, "Email ou mot de passe incorrect.")

    return render(request, "accounts/admin_login.html")


def logout_view(request):
    logout(request)
    return redirect("login")
