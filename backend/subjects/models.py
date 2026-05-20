from django.db import models


class Subject(models.Model):
    name = models.CharField(max_length=120)
    department = models.CharField(max_length=120, blank=True)
    study_year = models.CharField(max_length=80, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("department", "study_year", "name")
        constraints = [
            models.UniqueConstraint(fields=("name", "department", "study_year"), name="unique_subject_by_department_year"),
        ]

    def __str__(self):
        return self.name
