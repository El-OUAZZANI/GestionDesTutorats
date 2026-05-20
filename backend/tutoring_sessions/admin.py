from django.contrib import admin
from .models import Room, TutoringSession


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("name", "capacity", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(TutoringSession)
class TutoringSessionAdmin(admin.ModelAdmin):
    list_display = ("subject", "student", "tutor", "room", "start_datetime", "status")
    list_filter = ("status", "subject", "room")
    search_fields = ("student__username", "student__email", "tutor__username", "tutor__email", "subject__name")
    date_hierarchy = "start_datetime"
