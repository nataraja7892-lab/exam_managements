from django.db import models


class Student(models.Model):
    YEAR_CHOICES = [
        (1, 'First Year'),
        (2, 'Second Year'),
        (3, 'Third Year'),
        (4, 'Fourth Year'),
    ]

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    register_number = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    course = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    caste = models.CharField(max_length=50)
    dob = models.DateField()
    mobile_number = models.CharField(max_length=15)
    email = models.EmailField()
    year = models.IntegerField(choices=YEAR_CHOICES)

    def __str__(self):
        return f"{self.register_number} - {self.name}"
