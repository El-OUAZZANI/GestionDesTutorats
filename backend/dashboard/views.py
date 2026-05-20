from django.contrib import messages as django_messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from datetime import datetime, time, timedelta

from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST

from accounts.forms import StudentCreationForm, TutorApplicationForm
from accounts.models import AdminNotification, ContactAdminMessage, Profile, TutorApplication
from availability.models import Availability
from messages_app.models import Message
from notifications.models import Notification
from subjects.models import Subject
from tutoring_sessions.models import Room, TutoringSession


User = get_user_model()


DEFAULT_SUBJECTS = (
    ("Python", "Génie Informatique"),
    ("Java", "Génie Informatique"),
    ("Django", "Génie Informatique"),
    ("Algorithmique", "Génie Informatique"),
    ("Programmation web", "Génie Informatique"),
    ("Base de données", "Génie Informatique"),
    ("Réseaux", "Réseaux et Télécoms"),
    ("Mathématiques", "Génie Informatique"),
)

DEPARTMENTS = (
    "Ingénierie Informatique & Réseaux",
    "Ingénierie Automatisme et Informatique Industrielle",
    "Génie Industriel",
)

YEARS = ("1ère année", "2ème année", "3ème année", "4ème année", "5ème année")

WEEK_DAYS = (
    (0, "Lundi"),
    (1, "Mardi"),
    (2, "Mercredi"),
    (3, "Jeudi"),
    (4, "Vendredi"),
    (5, "Samedi"),
)

AVAILABILITY_SLOTS = (
    (time(8, 30), time(9, 15), "08:30 - 09:15"),
    (time(9, 15), time(10, 0), "09:15 - 10:00"),
    (time(10, 0), time(10, 45), "10:00 - 10:45"),
    (time(11, 0), time(11, 45), "11:00 - 11:45"),
    (time(14, 30), time(15, 15), "14:30 - 15:15"),
    (time(15, 15), time(16, 0), "15:15 - 16:00"),
    (time(16, 0), time(16, 45), "16:00 - 16:45"),
    (time(17, 0), time(17, 45), "17:00 - 17:45"),
)

SUBJECT_CATALOG = {
    "Ingénierie Informatique & Réseaux": {
        "1ère année": ("Analyse 1", "Algèbre 1", "Algorithmique 1", "Architecture des ordinateurs", "Électronique numérique", "Langage C"),
        "2ème année": ("Structures de données", "Programmation orientée objet Java", "Systèmes d'exploitation", "Bases de données relationnelles", "Réseaux informatiques 1", "Probabilités et statistiques"),
        "3ème année": ("Développement web", "Administration systèmes Linux", "Réseaux informatiques 2", "Génie logiciel UML", "Python avancé", "Bases de données avancées"),
        "4ème année": ("Django et frameworks web", "Sécurité informatique", "Cloud computing", "DevOps", "Data engineering", "Administration réseau avancée"),
        "5ème année": ("Architecture logicielle", "Cybersécurité avancée", "Intelligence artificielle", "Big Data", "Projet de fin d'études", "Management SI"),
    },
    "Ingénierie Automatisme et Informatique Industrielle": {
        "1ère année": ("Analyse 1", "Algèbre 1", "Physique appliquée", "Électricité générale", "Algorithmique 1", "Dessin industriel"),
        "2ème année": ("Automatique continue", "Électronique analogique", "Capteurs et instrumentation", "Programmation C", "Probabilités et statistiques", "Machines électriques"),
        "3ème année": ("Automates programmables industriels", "Supervision SCADA", "Systèmes embarqués", "Régulation industrielle", "Réseaux industriels", "Traitement du signal"),
        "4ème année": ("Robotique industrielle", "Commande numérique", "Informatique industrielle", "IoT industriel", "Maintenance industrielle", "Vision industrielle"),
        "5ème année": ("Automatisation avancée", "Industrie 4.0", "Sûreté de fonctionnement", "Jumeaux numériques", "Projet de fin d'études", "Management industriel"),
    },
    "Génie Industriel": {
        "1ère année": ("Analyse 1", "Algèbre 1", "Mécanique générale", "Introduction au génie industriel", "Informatique bureautique", "Dessin technique"),
        "2ème année": ("Recherche opérationnelle", "Statistiques industrielles", "Gestion de production", "Comptabilité analytique", "Méthodes numériques", "Résistance des matériaux"),
        "3ème année": ("Lean manufacturing", "Logistique et supply chain", "Gestion de la qualité", "Planification MRP", "Simulation des systèmes", "Gestion de maintenance"),
        "4ème année": ("Optimisation industrielle", "Management de la production", "ERP et systèmes d'information", "Six Sigma", "Gestion de projet industriel", "Ergonomie industrielle"),
        "5ème année": ("Stratégie industrielle", "Excellence opérationnelle", "Audit qualité", "Management des risques", "Projet de fin d'études", "Entrepreneuriat industriel"),
    },
}


def home(request):
    return render(request, "home.html")


def about(request):
    return render(request, "about.html")


def contact_admin(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip()
        request_type = request.POST.get("request_type", ContactAdminMessage.TYPE_ACCOUNT)
        message = request.POST.get("message", "").strip()

        if not full_name or not email or not message:
            django_messages.error(request, "Veuillez remplir le nom complet, l'email et le message.")
            return redirect("contact_admin")

        if request_type not in dict(ContactAdminMessage.REQUEST_TYPE_CHOICES):
            request_type = ContactAdminMessage.TYPE_OTHER

        contact_message = ContactAdminMessage.objects.create(
            full_name=full_name,
            email=email,
            request_type=request_type,
            message=message,
        )
        AdminNotification.objects.create(
            title="Nouveau message contact admin",
            content=f"{full_name} a envoye une demande : {contact_message.get_request_type_display()}.",
            contact_message=contact_message,
        )
        django_messages.success(request, "Votre demande a ete envoyee a l'administration.")
        return redirect("contact_admin")

    return render(request, "contact_admin.html")


def ensure_profile(user):
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile


def ensure_default_subjects():
    for department, years in SUBJECT_CATALOG.items():
        for study_year, subjects in years.items():
            for name in subjects:
                Subject.objects.get_or_create(
                    name=name,
                    department=department,
                    study_year=study_year,
                    defaults={"description": f"Matière de {study_year} - {department}"},
                )


def year_rank(value):
    return {
        "1ère année": 1,
        "2ème année": 2,
        "3ème année": 3,
        "4ème année": 4,
        "5ème année": 5,
    }.get(value, 0)


def allowed_subjects_for_profile(profile):
    if not profile.department or not profile.study_year:
        return Subject.objects.none()
    return Subject.objects.filter(department=profile.department, study_year=profile.study_year)


def teachable_subjects_for_profile(profile):
    if not profile.department or not profile.study_year:
        return Subject.objects.none()

    max_rank = year_rank(profile.study_year)
    allowed_years = [year for year in YEARS if year_rank(year) and year_rank(year) <= max_rank]
    return Subject.objects.filter(department=profile.department, study_year__in=allowed_years)


def current_week_start():
    today = timezone.localdate()
    return today - timedelta(days=today.weekday())


def next_bookable_week_start():
    week_start = current_week_start()
    if timezone.localdate() > week_start + timedelta(days=5):
        return week_start + timedelta(days=7)
    return week_start


def build_availability_grid(tutor, week_start):
    availabilities = {
        (availability.date, availability.start_time): availability
        for availability in Availability.objects.filter(tutor=tutor, date__gte=week_start, date__lte=week_start + timedelta(days=5))
        .select_related("subject", "room")
    }
    days = []
    for day_offset, day_name in WEEK_DAYS:
        current_day = week_start + timedelta(days=day_offset)
        cells = []
        for start_time, end_time, label in AVAILABILITY_SLOTS:
            availability = availabilities.get((current_day, start_time))
            cells.append(
                {
                    "value": f"{current_day.isoformat()}|{start_time.strftime('%H:%M')}|{end_time.strftime('%H:%M')}",
                    "label": label,
                    "availability": availability,
                }
            )
        days.append({"name": day_name, "date": current_day, "cells": cells})
    return days


def ensure_default_rooms():
    for name in ("Salle A101", "Salle A102", "Salle B201", "Salle B202", "Salle C301"):
        Room.objects.get_or_create(name=name, defaults={"capacity": 1})


def combine_aware(day, slot_time):
    return timezone.make_aware(datetime.combine(day, slot_time))


def room_is_available(room, start_datetime, end_datetime, exclude_availability_id=None):
    if TutoringSession.objects.filter(
        room=room,
        status__in=(TutoringSession.STATUS_PENDING, TutoringSession.STATUS_CONFIRMED),
        start_datetime__lt=end_datetime,
        end_datetime__gt=start_datetime,
    ).exists():
        return False

    assigned_availabilities = Availability.objects.filter(
        room=room,
        is_available=True,
        date=start_datetime.date(),
        start_time__lt=end_datetime.time(),
        end_time__gt=start_datetime.time(),
    )
    if exclude_availability_id:
        assigned_availabilities = assigned_availabilities.exclude(id=exclude_availability_id)
    return not assigned_availabilities.exists()


def build_admin_assignment_calendar(week_start, rooms):
    now = timezone.now()
    availabilities = (
        Availability.objects.filter(
            is_available=True,
            date__gte=week_start,
            date__lte=week_start + timedelta(days=5),
        )
        .select_related("tutor", "subject", "room")
        .order_by("date", "start_time", "tutor__first_name", "tutor__last_name")
    )
    grouped = {}
    for availability in availabilities:
        start_datetime = combine_aware(availability.date, availability.start_time)
        if start_datetime <= now:
            continue

        end_datetime = combine_aware(availability.date, availability.end_time)
        available_rooms = [room for room in rooms if room_is_available(room, start_datetime, end_datetime, availability.id)]
        grouped.setdefault((availability.date, availability.start_time), []).append(
            {
                "availability": availability,
                "rooms": available_rooms,
                "subjects": get_tutor_subjects(availability.tutor),
            }
        )

    days = []
    for day_offset, day_name in WEEK_DAYS:
        current_day = week_start + timedelta(days=day_offset)
        cells = []
        for start_time, end_time, label in AVAILABILITY_SLOTS:
            cells.append(
                {
                    "label": label,
                    "availabilities": grouped.get((current_day, start_time), []),
                }
            )
        days.append({"name": day_name, "date": current_day, "cells": cells})
    return days


def get_approved_tutor_application(user):
    return (
        TutorApplication.objects.filter(student=user, status=TutorApplication.STATUS_APPROVED)
        .prefetch_related("subjects")
        .first()
    )


def get_tutor_subjects(user):
    application = get_approved_tutor_application(user)
    return application.subjects.all() if application else Subject.objects.none()


def require_student_access(user):
    if user.is_staff or user.is_superuser:
        raise PermissionDenied("Les comptes administrateurs Django n'ont pas accès à l'espace étudiant.")

    profile = ensure_profile(user)
    if profile.is_platform_admin:
        raise PermissionDenied("Les comptes admin applicatifs n'ont pas accès à l'espace étudiant.")

    return profile


def require_tutor_access(user):
    if user.is_staff or user.is_superuser:
        raise PermissionDenied("Les comptes administrateurs Django n'ont pas accès à l'espace tuteur.")

    profile = ensure_profile(user)
    if profile.is_platform_admin:
        raise PermissionDenied("Les comptes admin applicatifs n'ont pas accès à l'espace tuteur.")
    if not profile.is_tutor:
        raise PermissionDenied("Votre demande tuteur doit être acceptée avant d'accéder à cet espace.")

    return profile


def require_admin_access(user):
    if user.is_staff or user.is_superuser:
        raise PermissionDenied("Utilisez /django-admin/ pour le compte admin Django.")

    profile = ensure_profile(user)
    if not profile.is_platform_admin:
        raise PermissionDenied("Accès réservé aux administrateurs applicatifs.")

    return profile


def calculate_profile_completion(user, profile):
    fields = (
        user.first_name,
        user.last_name,
        user.email,
        profile.department,
        profile.study_year,
        profile.phone,
        profile.bio,
    )
    completed = sum(1 for value in fields if value)
    return round((completed / len(fields)) * 100)


@login_required
def student_dashboard(request):
    profile = require_student_access(request.user)
    now = timezone.now()

    student_sessions = TutoringSession.objects.filter(student=request.user)
    upcoming_sessions = (
        student_sessions.filter(start_datetime__gte=now)
        .exclude(status__in=(
            TutoringSession.STATUS_COMPLETED,
            TutoringSession.STATUS_CANCELLED,
            TutoringSession.STATUS_REFUSED,
        ))
        .select_related("tutor", "subject")
        .order_by("start_datetime")[:3]
    )

    latest_application = TutorApplication.objects.filter(student=request.user).first()
    pending_tutor_application = TutorApplication.objects.filter(
        student=request.user,
        status=TutorApplication.STATUS_PENDING,
    ).first()

    return render(
        request,
        "student/dashboard.html",
        {
            "profile": profile,
            "upcoming_sessions": upcoming_sessions,
            "upcoming_sessions_count": student_sessions.filter(
                start_datetime__gte=now,
                status__in=(TutoringSession.STATUS_PENDING, TutoringSession.STATUS_CONFIRMED),
            ).count(),
            "completed_sessions_count": student_sessions.filter(status=TutoringSession.STATUS_COMPLETED).count(),
            "unread_messages_count": Message.objects.filter(receiver=request.user, is_read=False).count(),
            "unread_notifications_count": Notification.objects.filter(user=request.user, is_read=False).count(),
            "recent_notifications": Notification.objects.filter(user=request.user)[:3],
            "latest_application": latest_application,
            "pending_tutor_application": pending_tutor_application,
            "profile_completion": calculate_profile_completion(request.user, profile),
        },
    )


@login_required
def search_tutors(request):
    student_profile = require_student_access(request.user)
    ensure_default_subjects()

    query = request.GET.get("q", "").strip()
    subject_id = request.GET.get("subject", "")
    department = student_profile.department
    student_allowed_subjects = allowed_subjects_for_profile(student_profile)
    if subject_id and not student_allowed_subjects.filter(id=subject_id).exists():
        subject_id = ""

    selected_subject = student_allowed_subjects.filter(id=subject_id).first() if subject_id else None
    week_start = next_bookable_week_start()
    week_end = week_start + timedelta(days=5)
    now = timezone.now()

    available_slots_qs = Availability.objects.none()
    if selected_subject:
        available_slots_qs = (
            Availability.objects.filter(
                is_available=True,
                room__isnull=False,
                subject=selected_subject,
                date__gte=max(timezone.localdate(), week_start),
                date__lte=week_end,
            )
            .select_related("tutor", "tutor__profile", "room", "subject")
            .exclude(tutor__is_staff=True)
            .exclude(tutor__is_superuser=True)
            .exclude(tutor__profile__is_platform_admin=True)
            .distinct()
            .order_by("date", "start_time", "tutor__first_name", "tutor__last_name")
        )

        if query:
            available_slots_qs = available_slots_qs.filter(
                Q(tutor__first_name__icontains=query)
                | Q(tutor__last_name__icontains=query)
                | Q(tutor__username__icontains=query)
                | Q(tutor__email__icontains=query)
                | Q(room__name__icontains=query)
                | Q(subject__name__icontains=query)
            )

    existing_student_sessions = TutoringSession.objects.filter(
        student=request.user,
        status__in=(TutoringSession.STATUS_PENDING, TutoringSession.STATUS_CONFIRMED),
    )
    grouped_slots = {}
    for availability in available_slots_qs:
        start_datetime = combine_aware(availability.date, availability.start_time)
        if start_datetime <= now:
            continue

        grouped_slots.setdefault((availability.date, availability.start_time), []).append(availability)

    availability_days = []
    available_slots_count = 0
    for day_offset, day_name in WEEK_DAYS:
        current_day = week_start + timedelta(days=day_offset)
        cells = []
        for start_time, end_time, label in AVAILABILITY_SLOTS:
            start_datetime = combine_aware(current_day, start_time)
            end_datetime = combine_aware(current_day, end_time)
            tutor_slots = grouped_slots.get((current_day, start_time), [])
            reservable_slots = [slot for slot in tutor_slots if slot.tutor_id != request.user.id]
            has_conflict = existing_student_sessions.filter(
                start_datetime__lt=end_datetime,
                end_datetime__gt=start_datetime,
            ).exists()
            is_past = start_datetime <= now
            is_available = bool(reservable_slots) and not has_conflict and not is_past
            has_own_slot = bool(tutor_slots) and not reservable_slots
            if is_available:
                available_slots_count += 1

            cells.append(
                {
                    "label": label,
                    "availability": reservable_slots[0] if reservable_slots else None,
                    "tutors_count": len(reservable_slots),
                    "is_available": is_available,
                    "has_conflict": has_conflict,
                    "has_own_slot": has_own_slot,
                    "is_past": is_past,
                }
            )
        availability_days.append({"name": day_name, "date": current_day, "cells": cells})

    return render(
        request,
        "student/search_tutors.html",
        {
            "available_slots_count": available_slots_count,
            "availability_days": availability_days,
            "subjects": student_allowed_subjects,
            "selected_subject": subject_id,
            "selected_subject_obj": selected_subject,
            "selected_department": department,
            "query": query,
            "departments": DEPARTMENTS,
            "student_department": student_profile.department,
            "student_year": student_profile.study_year,
            "week_start": week_start,
            "week_end": week_end,
        },
    )


@login_required
@require_POST
def reserve_availability_session(request, availability_id):
    student_profile = require_student_access(request.user)
    availability = get_object_or_404(
        Availability.objects.select_related("tutor", "tutor__profile", "room"),
        id=availability_id,
        is_available=True,
        room__isnull=False,
    )
    subject = get_object_or_404(Subject, id=request.POST.get("subject"))

    if availability.tutor == request.user:
        django_messages.error(request, "Vous ne pouvez pas réserver une séance avec vous-même.")
        return redirect("search_tutors")

    if subject.department != student_profile.department or subject.study_year != student_profile.study_year:
        django_messages.error(request, "Cette matière ne correspond pas à votre filière ou à votre niveau.")
        return redirect("search_tutors")

    if availability.subject_id != subject.id:
        django_messages.error(request, "Cette matiere n'est pas affectee a ce creneau.")
        return redirect("search_tutors")

    if not get_tutor_subjects(availability.tutor).filter(id=subject.id).exists():
        django_messages.error(request, "Ce tuteur n'enseigne pas cette matière.")
        return redirect("search_tutors")

    start_datetime = combine_aware(availability.date, availability.start_time)
    end_datetime = combine_aware(availability.date, availability.end_time)
    if start_datetime <= timezone.now():
        django_messages.error(request, "Ce créneau n'est plus disponible.")
        return redirect("search_tutors")

    if TutoringSession.objects.filter(
        student=request.user,
        status__in=(TutoringSession.STATUS_PENDING, TutoringSession.STATUS_CONFIRMED),
        start_datetime__lt=end_datetime,
        end_datetime__gt=start_datetime,
    ).exists():
        django_messages.error(request, "Vous avez déjà une séance réservée sur ce même horaire.")
        return redirect("search_tutors")

    if not room_is_available(availability.room, start_datetime, end_datetime, availability.id):
        django_messages.error(request, "La salle de ce créneau n'est plus disponible.")
        return redirect("search_tutors")

    message = request.POST.get("message", "")
    TutoringSession.objects.create(
        tutor=availability.tutor,
        student=request.user,
        subject=subject,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        status=TutoringSession.STATUS_CONFIRMED,
        location=availability.room.name,
        room=availability.room,
        request_message=message,
    )
    availability.is_available = False
    availability.save(update_fields=["is_available"])

    Notification.objects.create(
        user=availability.tutor,
        title="Nouvelle séance réservée",
        content=f"{request.user.get_full_name() or request.user.username} a réservé votre créneau en {subject.name}.",
        notification_type=Notification.TYPE_SUCCESS,
        url="/dashboard/tutor/sessions/",
    )
    Notification.objects.create(
        user=request.user,
        title="Séance réservée",
        content=f"Votre séance en {subject.name} est confirmée en {availability.room.name}.",
        notification_type=Notification.TYPE_SUCCESS,
        url="/dashboard/student/sessions/",
    )
    django_messages.success(request, "Votre séance a été réservée avec succès.")
    return redirect("student_sessions")


@login_required
@require_POST
def reserve_tutor_session(request, tutor_id):
    require_student_access(request.user)
    django_messages.error(request, "Choisissez un créneau avec salle depuis la recherche de matières.")
    return redirect("search_tutors")


@login_required
def sessions(request):
    require_student_access(request.user)
    student_sessions = TutoringSession.objects.filter(student=request.user).select_related("tutor", "subject", "room")
    now = timezone.now()

    return render(
        request,
        "student/sessions.html",
        {
            "sessions": student_sessions,
            "upcoming_count": student_sessions.filter(start_datetime__gte=now).exclude(
                status__in=(TutoringSession.STATUS_COMPLETED, TutoringSession.STATUS_CANCELLED, TutoringSession.STATUS_REFUSED)
            ).count(),
            "pending_count": student_sessions.filter(status=TutoringSession.STATUS_PENDING).count(),
            "confirmed_count": student_sessions.filter(status=TutoringSession.STATUS_CONFIRMED).count(),
            "completed_count": student_sessions.filter(status=TutoringSession.STATUS_COMPLETED).count(),
        },
    )


@login_required
@require_POST
def cancel_student_session(request, session_id):
    require_student_access(request.user)
    session = get_object_or_404(TutoringSession, id=session_id, student=request.user)

    if session.status in (TutoringSession.STATUS_PENDING, TutoringSession.STATUS_CONFIRMED):
        session.status = TutoringSession.STATUS_CANCELLED
        session.save(update_fields=["status"])
        Notification.objects.create(
            user=session.tutor,
            title="Séance annulée",
            content=f"La séance {session.subject.name} avec {request.user.get_full_name() or request.user.username} a été annulée.",
            notification_type=Notification.TYPE_WARNING,
            url="/dashboard/tutor/sessions/",
        )
        django_messages.success(request, "La séance a été annulée.")
    else:
        django_messages.info(request, "Cette séance ne peut plus être annulée.")

    return redirect("student_sessions")


@login_required
def messages(request):
    require_student_access(request.user)
    return session_messages(request, role="student")


@login_required
def student_session_messages(request, session_id):
    require_student_access(request.user)
    return session_messages(request, role="student", session_id=session_id)


@login_required
def tutor_messages(request):
    require_tutor_access(request.user)
    return session_messages(request, role="tutor")


@login_required
def tutor_session_messages(request, session_id):
    require_tutor_access(request.user)
    return session_messages(request, role="tutor", session_id=session_id)


def session_messages(request, role, session_id=None):
    if role == "student":
        sessions_qs = TutoringSession.objects.filter(student=request.user).select_related("tutor", "student", "subject", "room")
        template_name = "student/messages.html"
        selected_session = sessions_qs.filter(id=session_id).first() if session_id else sessions_qs.first()
    else:
        sessions_qs = TutoringSession.objects.filter(tutor=request.user).select_related("tutor", "student", "subject", "room")
        template_name = "tutor/messages.html"
        selected_session = sessions_qs.filter(id=session_id).first() if session_id else sessions_qs.first()

    if session_id and selected_session is None:
        raise PermissionDenied("Vous n'avez pas accès à cette conversation.")

    if request.method == "POST":
        if not selected_session:
            django_messages.error(request, "Aucune session disponible pour envoyer un message.")
            return redirect("student_messages" if role == "student" else "tutor_messages")

        content = request.POST.get("content", "").strip()
        if not content:
            django_messages.error(request, "Veuillez saisir un message.")
            redirect_name = "student_session_messages" if role == "student" else "tutor_session_messages"
            return redirect(redirect_name, session_id=selected_session.id)

        receiver = selected_session.tutor if role == "student" else selected_session.student
        Message.objects.create(
            sender=request.user,
            receiver=receiver,
            session=selected_session,
            content=content,
        )
        Notification.objects.create(
            user=receiver,
            title="Nouveau message",
            content=f"{request.user.get_full_name() or request.user.username} vous a envoyé un message.",
            notification_type=Notification.TYPE_MESSAGE,
            url=(
                f"/dashboard/tutor/messages/{selected_session.id}/"
                if role == "student"
                else f"/dashboard/student/messages/{selected_session.id}/"
            ),
        )
        redirect_name = "student_session_messages" if role == "student" else "tutor_session_messages"
        return redirect(redirect_name, session_id=selected_session.id)

    if selected_session:
        Message.objects.filter(session=selected_session, receiver=request.user, is_read=False).update(is_read=True)

    sessions_list = list(sessions_qs)
    conversations = []
    for session in sessions_list:
        last_message = (
            Message.objects.filter(session=session)
            .select_related("sender", "receiver")
            .order_by("-timestamp")
            .first()
        )
        other = session.tutor if role == "student" else session.student
        unread_count = Message.objects.filter(session=session, receiver=request.user, is_read=False).count()
        conversations.append(
            {
                "session": session,
                "user": other,
                "last_message": last_message,
                "unread_count": unread_count,
            }
        )

    conversations.sort(
        key=lambda item: item["last_message"].timestamp if item["last_message"] else item["session"].start_datetime,
        reverse=True,
    )

    messages_qs = Message.objects.none()
    other_user = None
    if selected_session:
        other_user = selected_session.tutor if role == "student" else selected_session.student
        messages_qs = (
            Message.objects.filter(session=selected_session)
            .select_related("sender", "receiver", "session")
            .order_by("timestamp")
        )

    return render(
        request,
        template_name,
        {
            "conversations": conversations,
            "selected_session": selected_session,
            "other_user": other_user,
            "messages_list": messages_qs,
            "unread_messages_count": Message.objects.filter(receiver=request.user, is_read=False).count(),
        },
    )

@login_required
def notifications(request):
    require_student_access(request.user)
    notifications_qs = Notification.objects.filter(user=request.user)
    return render(
        request,
        "student/notifications.html",
        {
            "notifications": notifications_qs,
            "total_notifications": notifications_qs.count(),
            "unread_notifications": notifications_qs.filter(is_read=False).count(),
            "session_notifications": notifications_qs.filter(url__icontains="sessions").count(),
            "message_notifications": notifications_qs.filter(notification_type=Notification.TYPE_MESSAGE).count(),
        },
    )


@login_required
@require_POST
def mark_notifications_read(request):
    require_student_access(request.user)
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    django_messages.success(request, "Toutes les notifications ont été marquées comme lues.")
    return redirect("student_notifications")


@login_required
def profile(request):
    require_student_access(request.user)
    return render(request, "student/profile.html")


@login_required
def student_contact_admin(request):
    require_student_access(request.user)

    if request.method == "POST":
        request_type = request.POST.get("request_type", ContactAdminMessage.TYPE_OTHER)
        message = request.POST.get("message", "").strip()

        if request_type not in dict(ContactAdminMessage.REQUEST_TYPE_CHOICES):
            request_type = ContactAdminMessage.TYPE_OTHER

        if not message:
            django_messages.error(request, "Veuillez saisir votre message avant l'envoi.")
            return redirect("student_contact_admin")

        full_name = request.user.get_full_name() or request.user.get_username()
        email = request.user.email

        contact_message = ContactAdminMessage.objects.create(
            full_name=full_name,
            email=email,
            request_type=request_type,
            message=message,
        )
        AdminNotification.objects.create(
            title="Nouveau message etudiant",
            content=f"{full_name} a envoye une demande : {contact_message.get_request_type_display()}.",
            contact_message=contact_message,
        )
        return redirect("student_contact_admin_success")

    return render(
        request,
        "student/contact_admin.html",
        {
            "request_type_choices": ContactAdminMessage.REQUEST_TYPE_CHOICES,
        },
    )


@login_required
def student_contact_admin_success(request):
    require_student_access(request.user)
    return render(request, "student/contact_admin_success.html")


@login_required
@require_POST
def activate_tutor_mode(request):
    require_student_access(request.user)
    return redirect("tutor_application")


@login_required
def tutor_application(request):
    profile = require_student_access(request.user)
    ensure_default_subjects()

    if profile.is_tutor:
        return redirect("tutor_dashboard")

    pending_application = TutorApplication.objects.filter(
        student=request.user,
        status=TutorApplication.STATUS_PENDING,
    ).first()

    if request.method == "POST":
        if pending_application:
            django_messages.info(request, "Votre demande est déjà en attente de validation.")
            return redirect("tutor_application")

        form = TutorApplicationForm(request.POST, user=request.user)
        if form.is_valid():
            application = form.save(commit=False)
            application.student = request.user
            application.status = TutorApplication.STATUS_PENDING
            application.save()
            form.save_m2m()

            AdminNotification.objects.create(
                title="Nouvelle demande de tutorat",
                content=f"{request.user.get_full_name() or request.user.username} souhaite devenir tuteur.",
                tutor_application=application,
            )

            Notification.objects.create(
                user=request.user,
                title="Demande tuteur envoyée",
                content="Votre demande est en attente de validation par l'administration.",
                notification_type=Notification.TYPE_INFO,
                url="/dashboard/student/tutor-application/",
            )

            django_messages.success(
                request,
                "Votre demande a été envoyée à l'administration pour validation.",
            )
            return redirect("tutor_application")
    else:
        form = TutorApplicationForm(user=request.user)

    latest_application = TutorApplication.objects.filter(student=request.user).first()

    return render(
        request,
        "student/tutor_application.html",
        {
            "form": form,
            "pending_application": pending_application,
            "latest_application": latest_application,
            "subjects_catalog": Subject.objects.filter(department__in=DEPARTMENTS, study_year__in=YEARS),
            "selected_subject_ids": [int(value) for value in request.POST.getlist("subjects") if value.isdigit()],
        },
    )


@login_required
def tutor_dashboard(request):
    profile = require_tutor_access(request.user)
    now = timezone.now()
    tutor_sessions_qs = TutoringSession.objects.filter(tutor=request.user).select_related("student", "subject", "room")
    confirmed_sessions = tutor_sessions_qs.filter(status=TutoringSession.STATUS_CONFIRMED)
    available_slots = Availability.objects.filter(tutor=request.user, is_available=True, room__isnull=False).select_related("room")
    subjects = get_tutor_subjects(request.user)

    return render(
        request,
        "tutor/dashboard.html",
        {
            "profile": profile,
            "upcoming_sessions": confirmed_sessions.filter(start_datetime__gte=now).order_by("start_datetime")[:3],
            "available_slots": available_slots.order_by("date", "start_time")[:3],
            "reserved_count": confirmed_sessions.count(),
            "confirmed_count": confirmed_sessions.count(),
            "availability_count": available_slots.count(),
            "subjects": subjects,
            "subjects_count": subjects.count(),
        },
    )


@login_required
def tutor_requests(request):
    require_tutor_access(request.user)
    return redirect("tutor_sessions")


@login_required
def tutor_calendar(request):
    require_tutor_access(request.user)
    sessions_qs = TutoringSession.objects.filter(tutor=request.user).select_related("student", "subject").order_by("start_datetime")
    availabilities = Availability.objects.filter(tutor=request.user).select_related("subject")
    return render(
        request,
        "tutor/calendar.html",
        {
            "sessions": sessions_qs[:12],
            "availabilities": availabilities[:12],
            "available_count": availabilities.filter(is_available=True).count(),
            "confirmed_count": sessions_qs.filter(status=TutoringSession.STATUS_CONFIRMED).count(),
            "completed_count": sessions_qs.filter(status=TutoringSession.STATUS_COMPLETED).count(),
            "unavailable_count": availabilities.filter(is_available=False).count(),
        },
    )


@login_required
def tutor_availabilities(request):
    profile = require_tutor_access(request.user)
    week_start = next_bookable_week_start()

    if request.method == "POST":
        mode = Availability.MODE_IN_PERSON
        selected_slots = request.POST.getlist("slots")

        if not selected_slots:
            django_messages.error(request, "Veuillez sélectionner au moins un créneau.")
            return redirect("tutor_availabilities")

        try:
            first_slot = selected_slots[0]
            start_date_value, start_time_value, end_time_value = first_slot.split("|")
            start_date = datetime.strptime(start_date_value, "%Y-%m-%d").date()
            start = datetime.strptime(start_time_value, "%H:%M").time()
            end = datetime.strptime(end_time_value, "%H:%M").time()
        except (TypeError, ValueError, IndexError):
            django_messages.error(request, "Veuillez saisir une date et des heures valides.")
            return redirect("tutor_availabilities")

        if end <= start:
            django_messages.error(request, "L'heure de fin doit être après l'heure de début.")
            return redirect("tutor_availabilities")

        for slot_value in selected_slots:
            try:
                date_value, start_value, end_value = slot_value.split("|")
                slot_date = datetime.strptime(date_value, "%Y-%m-%d").date()
                slot_start = datetime.strptime(start_value, "%H:%M").time()
                slot_end = datetime.strptime(end_value, "%H:%M").time()
            except (TypeError, ValueError):
                continue

            Availability.objects.update_or_create(
                tutor=request.user,
                date=slot_date,
                start_time=slot_start,
                defaults={
                    "subject": None,
                    "end_time": slot_end,
                    "mode": mode,
                    "location": "",
                    "is_available": True,
                },
            )
        django_messages.success(request, "Disponibilité ajoutée.")
        return redirect("tutor_availabilities")

    return render(
        request,
        "tutor/availabilities.html",
        {
            "profile": profile,
            "availabilities": Availability.objects.filter(tutor=request.user).select_related("subject"),
            "availability_days": build_availability_grid(request.user, week_start),
            "week_start": week_start,
            "week_end": week_start + timedelta(days=5),
        },
    )


@login_required
def tutor_subjects(request):
    profile = require_tutor_access(request.user)
    application = get_approved_tutor_application(request.user)
    allowed_subjects = teachable_subjects_for_profile(profile)
    subjects = get_tutor_subjects(request.user)

    if request.method == "POST":
        selected_subjects = allowed_subjects.filter(id__in=request.POST.getlist("subjects"))
        if application:
            application.subjects.set(selected_subjects)
            django_messages.success(request, "Vos matières enseignées ont été mises à jour.")
        else:
            django_messages.error(request, "Aucune demande tuteur approuvée n'est liée à ce compte.")
        return redirect("tutor_subjects")

    return render(
        request,
        "tutor/subjects.html",
        {
            "profile": profile,
            "application": application,
            "allowed_subjects": allowed_subjects,
            "subjects": subjects,
            "selected_subject_ids": list(subjects.values_list("id", flat=True)),
        },
    )


@login_required
def tutor_sessions(request):
    require_tutor_access(request.user)
    all_sessions = TutoringSession.objects.filter(tutor=request.user).select_related("student", "subject", "room")
    assigned_availabilities = Availability.objects.filter(
        tutor=request.user,
        is_available=True,
        room__isnull=False,
    ).select_related("room", "subject")
    status_filter = request.GET.get("status", "all")
    sessions_qs = all_sessions
    if status_filter in (
        TutoringSession.STATUS_PENDING,
        TutoringSession.STATUS_CONFIRMED,
        TutoringSession.STATUS_COMPLETED,
        TutoringSession.STATUS_CANCELLED,
        TutoringSession.STATUS_REFUSED,
    ):
        sessions_qs = sessions_qs.filter(status=status_filter)

    return render(
        request,
        "tutor/sessions.html",
        {
            "sessions": sessions_qs,
            "assigned_availabilities": assigned_availabilities if status_filter in ("all", TutoringSession.STATUS_PENDING) else [],
            "status_filter": status_filter,
            "available_count": assigned_availabilities.count(),
            "confirmed_count": all_sessions.filter(status=TutoringSession.STATUS_CONFIRMED).count(),
            "completed_count": all_sessions.filter(status=TutoringSession.STATUS_COMPLETED).count(),
            "cancelled_count": all_sessions.filter(status=TutoringSession.STATUS_CANCELLED).count(),
        },
    )


@login_required
@require_POST
def tutor_review_session(request, session_id, decision):
    require_tutor_access(request.user)
    django_messages.info(request, "Les séances sont confirmées automatiquement dès la réservation d'un créneau.")
    return redirect("tutor_sessions")


@login_required
@require_POST
def tutor_complete_session(request, session_id):
    require_tutor_access(request.user)
    session = get_object_or_404(TutoringSession, id=session_id, tutor=request.user)

    if session.status == TutoringSession.STATUS_CONFIRMED:
        session.status = TutoringSession.STATUS_COMPLETED
        session.save(update_fields=["status"])
        Notification.objects.create(
            user=session.student,
            title="Session terminée",
            content=f"Votre séance en {session.subject.name} est marquée comme terminée.",
            notification_type=Notification.TYPE_SUCCESS,
            url="/dashboard/student/sessions/",
        )
        django_messages.success(request, "Session marquée comme terminée.")
    else:
        django_messages.info(request, "Seules les sessions confirmées peuvent être terminées.")

    return redirect("tutor_sessions")


@login_required
@require_POST
def tutor_toggle_availability(request, availability_id):
    require_tutor_access(request.user)
    availability = get_object_or_404(Availability, id=availability_id, tutor=request.user)
    availability.is_available = not availability.is_available
    availability.save(update_fields=["is_available"])
    django_messages.success(request, "Disponibilité mise à jour.")
    return redirect("tutor_availabilities")


@login_required
@never_cache
def admin_dashboard(request):
    require_admin_access(request.user)
    pending_applications = TutorApplication.objects.filter(status=TutorApplication.STATUS_PENDING)
    students = User.objects.filter(is_staff=False, is_superuser=False, profile__is_platform_admin=False)
    unread_notifications = AdminNotification.objects.filter(is_read=False)
    unread_contact_messages = ContactAdminMessage.objects.filter(is_read=False)

    return render(
        request,
        "admin_panel/dashboard.html",
        {
            "pending_applications": pending_applications[:5],
            "pending_count": pending_applications.count(),
            "student_count": students.count(),
            "tutor_count": students.filter(profile__is_tutor=True).count(),
            "unread_count": unread_notifications.count(),
            "unread_contact_count": unread_contact_messages.count(),
            "recent_contact_messages": ContactAdminMessage.objects.all()[:4],
        },
    )


@login_required
@never_cache
def admin_students(request):
    require_admin_access(request.user)
    students = (
        User.objects.filter(is_staff=False, is_superuser=False, profile__is_platform_admin=False)
        .select_related("profile")
        .order_by("first_name", "last_name", "username")
    )
    return render(request, "admin_panel/students.html", {"students": students})


@login_required
@require_POST
def admin_toggle_student_active(request, student_id):
    require_admin_access(request.user)
    student = User.objects.get(id=student_id, is_staff=False, is_superuser=False)
    student.is_active = not student.is_active
    student.save(update_fields=["is_active"])
    django_messages.success(request, "Statut du compte étudiant mis à jour.")
    return redirect("admin_students")


@login_required
@require_POST
def admin_toggle_student_tutor(request, student_id):
    require_admin_access(request.user)
    student = User.objects.get(id=student_id, is_staff=False, is_superuser=False)
    profile = ensure_profile(student)

    if not profile.is_tutor and (not profile.department or not profile.study_year):
        django_messages.error(request, "Renseignez la filière et l'année de l'étudiant avant d'activer le mode tuteur.")
        return redirect("admin_students")

    profile.is_tutor = not profile.is_tutor
    profile.save(update_fields=["is_tutor", "updated_at"])

    if profile.is_tutor and not TutorApplication.objects.filter(
        student=student,
        status=TutorApplication.STATUS_APPROVED,
    ).exists():
        TutorApplication.objects.create(
            student=student,
            department=profile.department,
            level=profile.study_year,
            session_mode="in_person",
            motivation="Activation directe par l'administration applicative.",
            status=TutorApplication.STATUS_APPROVED,
            reviewed_by=request.user,
            reviewed_at=timezone.now(),
        )

    django_messages.success(request, "Statut tuteur mis à jour.")
    return redirect("admin_students")


@login_required
@never_cache
def admin_create_student(request):
    require_admin_access(request.user)

    if request.method == "POST":
        form = StudentCreationForm(request.POST)
        if form.is_valid():
            form.save()
            django_messages.success(request, "Étudiant ajouté avec succès.")
            return redirect("admin_students")
    else:
        form = StudentCreationForm()

    return render(request, "admin_panel/create_student.html", {"form": form})


@login_required
@never_cache
def admin_tutors(request):
    require_admin_access(request.user)
    tutors = User.objects.filter(profile__is_tutor=True).select_related("profile")
    return render(request, "admin_panel/tutors.html", {"tutors": tutors})


@login_required
@never_cache
def admin_subjects(request):
    require_admin_access(request.user)
    ensure_default_subjects()
    return render(
        request,
        "admin_panel/subjects.html",
        {"subjects": Subject.objects.filter(department__in=DEPARTMENTS, study_year__in=YEARS)},
    )


@login_required
@never_cache
def admin_sessions(request):
    require_admin_access(request.user)
    ensure_default_rooms()

    if request.method == "POST":
        availability = get_object_or_404(
            Availability.objects.select_related("tutor", "subject"),
            id=request.POST.get("availability"),
            is_available=True,
        )
        room = get_object_or_404(Room, id=request.POST.get("room"), is_active=True)
        subject = get_object_or_404(Subject, id=request.POST.get("subject"))
        start_datetime = combine_aware(availability.date, availability.start_time)
        end_datetime = combine_aware(availability.date, availability.end_time)

        if start_datetime <= timezone.now():
            django_messages.error(request, "Impossible d'affecter un creneau deja passe.")
            return redirect("admin_sessions")

        if not get_tutor_subjects(availability.tutor).filter(id=subject.id).exists():
            django_messages.error(request, "Ce tuteur n'enseigne pas cette matiere.")
            return redirect("admin_sessions")

        if not room_is_available(room, start_datetime, end_datetime, availability.id):
            django_messages.error(request, "Cette salle est déjà occupée sur ce créneau.")
            return redirect("admin_sessions")

        availability.subject = subject
        availability.room = room
        availability.location = room.name
        availability.save(update_fields=["subject", "room", "location"])
        Notification.objects.create(
            user=availability.tutor,
            title="Salle affectée",
            content=f"Votre disponibilité du {availability.date:%d/%m} à {availability.start_time:%H:%M} a été affectée en {room.name}.",
            notification_type=Notification.TYPE_SUCCESS,
            url="/dashboard/tutor/availabilities/",
        )
        django_messages.success(request, "Salle affectée avec succès.")
        return redirect("admin_sessions")

    week_start = next_bookable_week_start()
    rooms = list(Room.objects.filter(is_active=True))

    sessions_qs = TutoringSession.objects.select_related("tutor", "student", "subject", "room")
    return render(
        request,
        "admin_panel/sessions.html",
        {
            "assignment_days": build_admin_assignment_calendar(week_start, rooms),
            "rooms": rooms,
            "sessions": sessions_qs[:12],
            "week_start": week_start,
            "week_end": week_start + timedelta(days=5),
        },
    )


@login_required
@never_cache
def admin_requests(request):
    require_admin_access(request.user)
    applications = TutorApplication.objects.select_related("student", "reviewed_by").prefetch_related("subjects")
    AdminNotification.objects.filter(tutor_application__isnull=False, is_read=False).update(is_read=True)
    return render(request, "admin_panel/requests.html", {"applications": applications})


@login_required
@never_cache
def admin_notifications(request):
    require_admin_access(request.user)
    notifications_qs = AdminNotification.objects.filter(contact_message__isnull=False).select_related("contact_message")
    notifications = list(notifications_qs)
    contact_messages = list(ContactAdminMessage.objects.all())

    AdminNotification.objects.filter(contact_message__isnull=False, is_read=False).update(is_read=True)
    ContactAdminMessage.objects.filter(is_read=False).update(is_read=True)

    return render(
        request,
        "admin_panel/notifications.html",
        {
            "notifications": notifications,
            "contact_messages": contact_messages,
            "total_notifications": len(notifications),
            "contact_count": len(contact_messages),
        },
    )


@login_required
@require_POST
def admin_review_tutor_application(request, application_id, decision):
    require_admin_access(request.user)
    application = TutorApplication.objects.select_related("student").get(id=application_id)

    if application.status != TutorApplication.STATUS_PENDING:
        django_messages.info(request, "Cette demande a déjà été traitée.")
        return redirect("admin_requests")

    application.reviewed_by = request.user
    application.reviewed_at = timezone.now()
    application.admin_note = request.POST.get("admin_note", "")

    if decision == "approve":
        application.status = TutorApplication.STATUS_APPROVED
        profile = ensure_profile(application.student)
        profile.is_tutor = True
        profile.department = application.department
        profile.study_year = application.level
        profile.save(update_fields=["is_tutor", "department", "study_year", "updated_at"])
        Notification.objects.create(
            user=application.student,
            title="Demande tuteur acceptée",
            content="Votre mode tuteur est maintenant activé.",
            notification_type=Notification.TYPE_SUCCESS,
            url="/dashboard/student/",
        )
        django_messages.success(request, "Demande acceptée. L'étudiant est maintenant tuteur.")
    elif decision == "reject":
        application.status = TutorApplication.STATUS_REJECTED
        Notification.objects.create(
            user=application.student,
            title="Demande tuteur refusée",
            content="Votre demande de passage en mode tuteur a été refusée.",
            notification_type=Notification.TYPE_WARNING,
            url="/dashboard/student/tutor-application/",
        )
        django_messages.success(request, "Demande refusée.")
    else:
        raise PermissionDenied("Décision invalide.")

    application.save(update_fields=["status", "admin_note", "reviewed_by", "reviewed_at", "updated_at"])
    return redirect("admin_requests")


@login_required
@never_cache
def admin_archives(request):
    require_admin_access(request.user)
    applications = TutorApplication.objects.exclude(status=TutorApplication.STATUS_PENDING)
    return render(request, "admin_panel/archive.html", {"applications": applications})
