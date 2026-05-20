from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import AdminNotification, ContactAdminMessage, Profile, TutorApplication

User = get_user_model()


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    extra = 0
    fields = ("is_platform_admin", "is_tutor", "department", "study_year", "phone", "bio")


@admin.action(description="Activer le mode tuteur")
def activate_tutor_mode(modeladmin, request, queryset):
    for user in queryset:
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.is_tutor = True
        profile.save(update_fields=["is_tutor", "updated_at"])


@admin.action(description="Désactiver le mode tuteur")
def deactivate_tutor_mode(modeladmin, request, queryset):
    for user in queryset:
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.is_tutor = False
        profile.save(update_fields=["is_tutor", "updated_at"])


@admin.action(description="Rendre admin/staff")
def make_staff(modeladmin, request, queryset):
    queryset.update(is_staff=True)


@admin.action(description="Retirer le statut admin/staff")
def remove_staff(modeladmin, request, queryset):
    queryset.update(is_staff=False, is_superuser=False)


@admin.action(description="Rendre admin applicatif")
def make_platform_admin(modeladmin, request, queryset):
    for user in queryset:
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.is_platform_admin = True
        profile.save(update_fields=["is_platform_admin", "updated_at"])


@admin.action(description="Retirer admin applicatif")
def remove_platform_admin(modeladmin, request, queryset):
    for user in queryset:
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.is_platform_admin = False
        profile.save(update_fields=["is_platform_admin", "updated_at"])


admin.site.unregister(User)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    inlines = (ProfileInline,)
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_platform_admin",
        "is_student",
        "is_tutor",
        "is_staff",
        "is_active",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "profile__is_platform_admin", "profile__is_tutor")
    search_fields = ("username", "email", "first_name", "last_name")
    actions = (
        activate_tutor_mode,
        deactivate_tutor_mode,
        make_platform_admin,
        remove_platform_admin,
        make_staff,
        remove_staff,
    )

    @admin.display(boolean=True, description="Admin app")
    def is_platform_admin(self, obj):
        profile, _ = Profile.objects.get_or_create(user=obj)
        return profile.is_platform_admin

    @admin.display(boolean=True, description="Étudiant")
    def is_student(self, obj):
        return not obj.is_staff

    @admin.display(boolean=True, description="Tuteur")
    def is_tutor(self, obj):
        profile, _ = Profile.objects.get_or_create(user=obj)
        return profile.is_tutor


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "user_email", "is_platform_admin", "is_tutor", "department", "study_year", "updated_at")
    list_filter = ("is_platform_admin", "is_tutor", "department", "study_year")
    search_fields = ("user__username", "user__email", "user__first_name", "user__last_name")
    list_editable = ("is_platform_admin", "is_tutor", "department", "study_year")

    @admin.display(description="Email")
    def user_email(self, obj):
        return obj.user.email


@admin.register(TutorApplication)
class TutorApplicationAdmin(admin.ModelAdmin):
    list_display = ("student", "department", "level", "status", "created_at", "reviewed_by")
    list_filter = ("status", "department", "level", "session_mode")
    search_fields = ("student__username", "student__email", "motivation", "experience")
    filter_horizontal = ("subjects",)


@admin.register(AdminNotification)
class AdminNotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "is_read", "created_at")
    list_filter = ("is_read",)
    search_fields = ("title", "content")


@admin.register(ContactAdminMessage)
class ContactAdminMessageAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "request_type", "is_read", "created_at")
    list_filter = ("request_type", "is_read")
    search_fields = ("full_name", "email", "message")


admin.site.site_header = "Administration GestionDesTutorats"
admin.site.site_title = "GestionDesTutorats Admin"
admin.site.index_title = "Gestion des utilisateurs et tutorats"
