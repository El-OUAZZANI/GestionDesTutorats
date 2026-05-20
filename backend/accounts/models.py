from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from subjects.models import Subject


DEPARTMENT_CHOICES = (
    ("Ingénierie Informatique & Réseaux", "Ingénierie Informatique & Réseaux"),
    ("Ingénierie Automatisme et Informatique Industrielle", "Ingénierie Automatisme et Informatique Industrielle"),
    ("Génie Industriel", "Génie Industriel"),
)

YEAR_CHOICES = (
    ("1ère année", "1ère année"),
    ("2ème année", "2ème année"),
    ("3ème année", "3ème année"),
    ("4ème année", "4ème année"),
    ("5ème année", "5ème année"),
)


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    is_platform_admin = models.BooleanField(default=False)
    is_tutor = models.BooleanField(default=False)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    department = models.CharField(max_length=120, choices=DEPARTMENT_CHOICES, blank=True)
    study_year = models.CharField(max_length=80, choices=YEAR_CHOICES, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profil de {self.user.get_username()}"


class TutorApplication(models.Model):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"

    STATUS_CHOICES = (
        (STATUS_PENDING, "En attente"),
        (STATUS_APPROVED, "Acceptée"),
        (STATUS_REJECTED, "Refusée"),
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tutor_applications",
    )
    department = models.CharField(max_length=120, choices=DEPARTMENT_CHOICES)
    level = models.CharField(max_length=80, choices=YEAR_CHOICES)
    session_mode = models.CharField(
        max_length=30,
        choices=(
            ("in_person", "Présentiel"),
        ),
        default="in_person",
    )
    subjects = models.ManyToManyField(Subject, related_name="tutor_applications")
    experience = models.TextField(blank=True)
    motivation = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    admin_note = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_tutor_applications",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Demande tuteur de {self.student.get_username()} - {self.get_status_display()}"


class AdminNotification(models.Model):
    title = models.CharField(max_length=160)
    content = models.TextField()
    tutor_application = models.ForeignKey(
        TutorApplication,
        on_delete=models.CASCADE,
        related_name="admin_notifications",
        null=True,
        blank=True,
    )
    contact_message = models.ForeignKey(
        "ContactAdminMessage",
        on_delete=models.CASCADE,
        related_name="admin_notifications",
        null=True,
        blank=True,
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.title


class ContactAdminMessage(models.Model):
    TYPE_ACCOUNT = "account"
    TYPE_TUTOR = "tutor"
    TYPE_LOGIN = "login"
    TYPE_ACCOUNT_INFO = "account_info"
    TYPE_OTHER = "other"

    REQUEST_TYPE_CHOICES = (
        (TYPE_ACCOUNT_INFO, "Informations de compte incorrectes"),
        (TYPE_OTHER, "Autre demande"),

    )

    full_name = models.CharField(max_length=160)
    email = models.EmailField()
    request_type = models.CharField(max_length=30, choices=REQUEST_TYPE_CHOICES, default=TYPE_ACCOUNT)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.full_name} - {self.get_request_type_display()}"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
