from django.conf import settings
from django.db import models


class Notification(models.Model):
    TYPE_INFO = "info"
    TYPE_SUCCESS = "success"
    TYPE_WARNING = "warning"
    TYPE_MESSAGE = "message"

    TYPE_CHOICES = (
        (TYPE_INFO, "Information"),
        (TYPE_SUCCESS, "Succès"),
        (TYPE_WARNING, "Alerte"),
        (TYPE_MESSAGE, "Message"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=160)
    content = models.TextField()
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default=TYPE_INFO)
    url = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.title
