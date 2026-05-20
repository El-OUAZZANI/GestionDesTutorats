from django.contrib import admin
from .models import Subject


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "department", "study_year", "created_at")
    list_filter = ("department", "study_year")
    search_fields = ("name", "department", "study_year", "description")

# Register your models here.
