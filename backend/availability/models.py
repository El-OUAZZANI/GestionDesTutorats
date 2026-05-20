from django.conf import settings
from django.db import models

from subjects.models import Subject
from tutoring_sessions.models import Room


class Availability(models.Model):
    MODE_IN_PERSON = "in_person"

    MODE_CHOICES = (
        (MODE_IN_PERSON, "Présentiel"),
    )

    tutor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="availabilities")
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name="availabilities")
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    mode = models.CharField(max_length=30, choices=MODE_CHOICES, default=MODE_IN_PERSON)
    location = models.CharField(max_length=255, blank=True)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, related_name="availabilities")
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("date", "start_time")

    def __str__(self):
        return f"{self.tutor} - {self.subject} - {self.date} {self.start_time}"
