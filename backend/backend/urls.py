"""
URL configuration for backend project.
"""

from django.contrib import admin
from django.urls import path, include
from dashboard.views import about, contact_admin, home

urlpatterns = [
    path('django-admin/', admin.site.urls),

    path("", home, name="home"),
    path("about/", about, name="about"),
    path("contact-admin/", contact_admin, name="contact_admin"),

    path("accounts/", include("accounts.urls")),
    path("dashboard/", include("dashboard.urls")),
]

# Pages d'erreur personnalisées
handler404 = "backend.views.error_404"
handler403 = "backend.views.error_403"
handler500 = "backend.views.error_500"