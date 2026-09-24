import random
from datetime import timedelta, time

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import DEPARTMENT_CHOICES, YEAR_CHOICES, Profile, TutorApplication, ContactAdminMessage
from subjects.models import Subject
from tutoring_sessions.models import Room, TutoringSession
from availability.models import Availability
from messages_app.models import Message
from notifications.models import Notification

User = get_user_model()

DEPARTMENTS = [d[0] for d in DEPARTMENT_CHOICES]
YEARS = [y[0] for y in YEAR_CHOICES]

SUBJECTS_BY_DEPARTMENT = {
    DEPARTMENTS[0]: ["Algorithmique", "Bases de données", "Réseaux", "Développement Web", "Systèmes d'exploitation"],
    DEPARTMENTS[1]: ["Automatisme industriel", "Électronique de puissance", "Robotique", "Systèmes embarqués"],
    DEPARTMENTS[2]: ["Gestion de production", "Qualité industrielle", "Logistique", "Supply chain"],
}

FIRST_NAMES = ["Yassine", "Karim", "Mehdi", "Imane", "Amine", "Khadija", "Youssef", "Salma", "Omar", "Fatima Zahra",
               "Hamza", "Nour", "Anas", "Rania", "Zakaria", "Meryem", "Ilyas", "Hiba", "Soufiane", "Lina"]
LAST_NAMES = ["El Amrani", "Bennani", "Tazi", "Idrissi", "Fassi", "Alaoui", "Chraibi", "Benjelloun", "Cherkaoui",
              "Lahlou", "Zahidi", "Benali", "Raji", "Sbai", "Moutawakil"]


class Command(BaseCommand):
    help = "Génère des données de test pour la plateforme GestionDesTutorats"

    def add_arguments(self, parser):
        parser.add_argument("--flush", action="store_true", help="Supprime les données existantes avant de générer")

    def handle(self, *args, **options):
        if options["flush"]:
            self.stdout.write("Suppression des données existantes...")
            Message.objects.all().delete()
            Notification.objects.all().delete()
            TutoringSession.objects.all().delete()
            Availability.objects.all().delete()
            TutorApplication.objects.all().delete()
            ContactAdminMessage.objects.all().delete()
            Room.objects.all().delete()
            Subject.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()

        random.seed(42)

        admin = self.create_admin()
        subjects = self.create_subjects()
        rooms = self.create_rooms()
        tutors = self.create_tutors(subjects)
        students = self.create_students()
        self.create_tutor_applications(students, subjects)
        self.create_availabilities(tutors, subjects, rooms)
        sessions = self.create_sessions(tutors, students, subjects, rooms)
        self.create_messages(sessions)
        self.create_notifications(students + tutors)
        self.create_contact_messages()

        self.stdout.write(self.style.SUCCESS(
            f"Données générées : {len(tutors)} tuteurs, {len(students)} étudiants, "
            f"{subjects.count()} matières, {rooms.count()} salles, {sessions.__len__()} séances."
        ))

    def create_admin(self):
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={"email": "admin@emsi.ma", "is_staff": True, "is_superuser": True,
                      "first_name": "Admin", "last_name": "Plateforme"},
        )
        if created:
            admin.set_password("EmsiDemo2026!")
            admin.save()

        platform_admin, created = User.objects.get_or_create(
            username="platformadmin",
            defaults={"email": "platformadmin@emsi.ma", "first_name": "Admin", "last_name": "Plateforme",
                      "is_staff": False, "is_superuser": False},
        )
        if created:
            platform_admin.set_password("EmsiDemo2026!")
            platform_admin.save()
        Profile.objects.filter(user=platform_admin).update(is_platform_admin=True)

        return admin

    def create_subjects(self):
        for dept, names in SUBJECTS_BY_DEPARTMENT.items():
            for name in names:
                for year in random.sample(YEARS, k=3):
                    Subject.objects.get_or_create(
                        name=name, department=dept, study_year=year,
                        defaults={"description": f"Cours de {name} - {year}"},
                    )
        return Subject.objects.all()

    def create_rooms(self):
        for i in range(1, 9):
            Room.objects.get_or_create(name=f"Salle {i:02d}", defaults={"capacity": random.choice([1, 2, 4, 6])})
        return Room.objects.all()

    def _make_user(self, username, first_name, last_name, email):
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": email, "first_name": first_name, "last_name": last_name},
        )
        if created:
            user.set_password("Passer123!")
            user.save()
        return user

    def create_tutors(self, subjects):
        tutors = []
        names = list(zip(FIRST_NAMES[:12], LAST_NAMES[:12]))
        for idx, (first, last) in enumerate(names, start=1):
            username = f"tutor{idx}"
            user = self._make_user(username, first, last, f"{username}@emsi.ma")
            dept = random.choice(DEPARTMENTS)
            year = random.choice(YEARS[2:])
            Profile.objects.filter(user=user).update(
                is_tutor=True,
                department=dept,
                study_year=year,
                phone=f"06{random.randint(10000000, 99999999)}",
                bio=f"Tuteur en {dept}, passionné par la pédagogie.",
            )

            dept_subjects = subjects.filter(department=dept)
            application, _ = TutorApplication.objects.update_or_create(
                student=user,
                defaults={
                    "department": dept,
                    "level": year,
                    "experience": "Bon niveau académique, expérience de tutorat informel.",
                    "motivation": "Je souhaite aider mes camarades et renforcer mes connaissances.",
                    "status": TutorApplication.STATUS_APPROVED,
                    "reviewed_at": timezone.now(),
                },
            )
            if dept_subjects.exists():
                application.subjects.set(random.sample(list(dept_subjects), k=min(3, dept_subjects.count())))

            tutors.append(user)
        return tutors

    def create_students(self):
        students = []
        names = list(zip(FIRST_NAMES[8:], LAST_NAMES[5:]))
        for idx, (first, last) in enumerate(names, start=1):
            username = f"student{idx}"
            user = self._make_user(username, first, last, f"{username}@emsi.ma")
            Profile.objects.filter(user=user).update(
                department=random.choice(DEPARTMENTS),
                study_year=random.choice(YEARS),
                phone=f"06{random.randint(10000000, 99999999)}",
            )
            students.append(user)
        return students

    def create_tutor_applications(self, students, subjects):
        for student in random.sample(students, k=min(6, len(students))):
            dept = random.choice(DEPARTMENTS)
            dept_subjects = subjects.filter(department=dept)
            app = TutorApplication.objects.create(
                student=student,
                department=dept,
                level=random.choice(YEARS[2:]),
                experience="Bon niveau académique, expérience de tutorat informel.",
                motivation="Je souhaite aider mes camarades et renforcer mes connaissances.",
                status=random.choice([TutorApplication.STATUS_PENDING, TutorApplication.STATUS_APPROVED,
                                       TutorApplication.STATUS_REJECTED]),
            )
            if dept_subjects.exists():
                app.subjects.set(random.sample(list(dept_subjects), k=min(2, dept_subjects.count())))

    def create_availabilities(self, tutors, subjects, rooms):
        today = timezone.localdate()
        for tutor in tutors:
            tutor_subjects = subjects.filter(department=Profile.objects.get(user=tutor).department)
            if not tutor_subjects.exists():
                continue
            for i in range(5):
                day = today + timedelta(days=random.randint(1, 21))
                start_hour = random.choice([9, 10, 11, 14, 15, 16])
                Availability.objects.create(
                    tutor=tutor,
                    subject=random.choice(list(tutor_subjects)),
                    date=day,
                    start_time=time(start_hour, 0),
                    end_time=time(start_hour + 1, 0),
                    location="Campus EMSI",
                    room=random.choice(list(rooms)),
                    is_available=True,
                )

    def create_sessions(self, tutors, students, subjects, rooms):
        sessions = []
        now = timezone.now()
        statuses = [TutoringSession.STATUS_PENDING, TutoringSession.STATUS_CONFIRMED,
                    TutoringSession.STATUS_COMPLETED, TutoringSession.STATUS_CANCELLED]
        for i in range(20):
            tutor = random.choice(tutors)
            student = random.choice(students)
            dept = Profile.objects.get(user=tutor).department
            dept_subjects = subjects.filter(department=dept)
            if not dept_subjects.exists():
                continue
            subject = random.choice(list(dept_subjects))
            offset_days = random.randint(-10, 15)
            start_hour = random.choice([9, 10, 11, 14, 15, 16])
            naive_dt = timezone.datetime.combine(now.date() + timedelta(days=offset_days), time(start_hour, 0))
            start_dt = timezone.make_aware(naive_dt)
            session = TutoringSession.objects.create(
                tutor=tutor,
                student=student,
                subject=subject,
                start_datetime=start_dt,
                end_datetime=start_dt + timedelta(hours=1),
                status=random.choice(statuses),
                location="Campus EMSI",
                room=random.choice(list(rooms)),
                request_message="Bonjour, je souhaiterais une séance sur ce sujet.",
            )
            sessions.append(session)
        return sessions

    def create_messages(self, sessions):
        for session in sessions[:12]:
            Message.objects.create(
                sender=session.student, receiver=session.tutor, session=session,
                content="Bonjour, est-il possible de confirmer la séance ?",
            )
            Message.objects.create(
                sender=session.tutor, receiver=session.student, session=session,
                content="Bonjour, c'est confirmé de mon côté, à bientôt !",
            )

    def create_notifications(self, users):
        for user in users:
            Notification.objects.create(
                user=user,
                title="Bienvenue sur la plateforme",
                content="Votre compte a été créé avec succès.",
                notification_type=Notification.TYPE_SUCCESS,
            )

    def create_contact_messages(self):
        ContactAdminMessage.objects.get_or_create(
            full_name="Yassine El Amrani",
            email="yassine.contact@emsi.ma",
            defaults={
                "request_type": ContactAdminMessage.TYPE_ACCOUNT_INFO,
                "message": "Mon département affiché est incorrect, pouvez-vous corriger ?",
            },
        )
