from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from register.models import Student
from django.core.exceptions import ValidationError


class Exam(models.Model):
    exam_title = models.CharField(max_length=100)
    exam_id = models.AutoField(primary_key=True)
    course = models.CharField(max_length=100)
    year = models.IntegerField(choices=[
        (1, 'First Year'),
        (2, 'Second Year'),
        (3, 'Third Year'),
        (4, 'Fourth Year')
    ])
    num_subjects = models.IntegerField()
    subject_names = models.JSONField(default=list)  # [{"name": "Math", "date": "2025-05-01"}, ...]
    subject_max_marks = models.JSONField(default=list)  # [{"name": "Math", "max_marks": 100}, ...]
    total_max_marks = models.IntegerField(default=0)  # Field to store the total max marks

    def __str__(self):
        return self.exam_title


# Signal to update total_max_marks when subject_max_marks is modified
@receiver(post_save, sender=Exam)
def update_total_max_marks(sender, instance, **kwargs):
    # Recalculate the total_max_marks based on subject_max_marks
    total_max_marks = sum(subject['max_marks'] for subject in instance.subject_max_marks)

    # If total_max_marks is different, update it
    if instance.total_max_marks != total_max_marks:
        instance.total_max_marks = total_max_marks
        instance.save()


class Result(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject_marks = models.JSONField(default=dict)  # Store marks for subjects in JSON format

    def __str__(self):
        return f"{self.student.name} - {self.exam.exam_title}"

    # ✅ Added validation
    def clean(self):
        subject_max_marks = {sub["name"]: sub["max_marks"] for sub in self.exam.subject_max_marks}

        for subject, mark in self.subject_marks.items():
            if subject in subject_max_marks:
                if mark > subject_max_marks[subject]:
                    raise ValidationError(f"{subject}: Marks cannot exceed {subject_max_marks[subject]}")
                if mark < 0:
                    raise ValidationError(f"{subject}: Marks cannot be negative")

    # ✅ Ensure validation always runs before saving
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
