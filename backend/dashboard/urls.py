from django.urls import path
from . import views


urlpatterns = [
    # Espace étudiant
    path("student/", views.student_dashboard, name="student_dashboard"),
    path("student/search-tutors/", views.search_tutors, name="search_tutors"),
    path("student/availabilities/<int:availability_id>/reserve/", views.reserve_availability_session, name="reserve_availability_session"),
    path("student/search-tutors/<int:tutor_id>/reserve/", views.reserve_tutor_session, name="reserve_tutor_session"),
    path("student/sessions/", views.sessions, name="student_sessions"),
    path("student/sessions/<int:session_id>/cancel/", views.cancel_student_session, name="cancel_student_session"),
    path("student/messages/", views.messages, name="student_messages"),
    path("student/messages/<int:session_id>/", views.student_session_messages, name="student_session_messages"),
    path("student/notifications/", views.notifications, name="student_notifications"),
    path("student/notifications/mark-read/", views.mark_notifications_read, name="mark_notifications_read"),
    path("student/profile/", views.profile, name="student_profile"),
    path("student/contact-admin/", views.student_contact_admin, name="student_contact_admin"),
    path("student/contact-admin/success/", views.student_contact_admin_success, name="student_contact_admin_success"),
    path("student/activate-tutor/", views.activate_tutor_mode, name="activate_tutor_mode"),
    path("student/tutor-application/", views.tutor_application, name="tutor_application"),

    # Espace tuteur
    path("tutor/", views.tutor_dashboard, name="tutor_dashboard"),
    path("tutor/requests/", views.tutor_requests, name="tutor_requests"),
    path("tutor/calendar/", views.tutor_calendar, name="tutor_calendar"),
    path("tutor/availabilities/", views.tutor_availabilities, name="tutor_availabilities"),
    path("tutor/availabilities/<int:availability_id>/toggle/", views.tutor_toggle_availability, name="tutor_toggle_availability"),
    path("tutor/subjects/", views.tutor_subjects, name="tutor_subjects"),
    path("tutor/sessions/", views.tutor_sessions, name="tutor_sessions"),
    path("tutor/sessions/<int:session_id>/complete/", views.tutor_complete_session, name="tutor_complete_session"),
    path("tutor/messages/", views.tutor_messages, name="tutor_messages"),
    path("tutor/messages/<int:session_id>/", views.tutor_session_messages, name="tutor_session_messages"),
    path("tutor/requests/<int:session_id>/<str:decision>/", views.tutor_review_session, name="tutor_review_session"),

    # Espace admin applicatif
    path("admin-panel/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-panel/students/", views.admin_students, name="admin_students"),
    path("admin-panel/students/create/", views.admin_create_student, name="admin_create_student"),
    path("admin-panel/students/<int:student_id>/toggle-active/", views.admin_toggle_student_active, name="admin_toggle_student_active"),
    path("admin-panel/students/<int:student_id>/toggle-tutor/", views.admin_toggle_student_tutor, name="admin_toggle_student_tutor"),
    path("admin-panel/tutors/", views.admin_tutors, name="admin_tutors"),
    path("admin-panel/subjects/", views.admin_subjects, name="admin_subjects"),
    path("admin-panel/sessions/", views.admin_sessions, name="admin_sessions"),
    path("admin-panel/notifications/", views.admin_notifications, name="admin_notifications"),
    path("admin-panel/requests/", views.admin_requests, name="admin_requests"),
    path(
        "admin-panel/requests/<int:application_id>/<str:decision>/",
        views.admin_review_tutor_application,
        name="admin_review_tutor_application",
    ),
    path("admin-panel/archives/", views.admin_archives, name="admin_archives"),
]
