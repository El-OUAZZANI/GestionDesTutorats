from django.contrib import admin
from .models import Availability


@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ("tutor", "subject", "date", "start_time", "end_time", "mode", "is_available")
    list_filter = ("mode", "is_available", "subject")
    search_fields = ("tutor__username", "tutor__email", "subject__name", "location")
