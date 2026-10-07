import datetime
from django.db import models
from django.contrib.auth.models import User


class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    allowed_levels = models.CharField(max_length=255, help_text="Comma-separated levels (e.g. Senior 1, Senior 2)")
    subjects_taught = models.CharField(max_length=255, default="General", help_text="Subjects taught by this teacher (e.g. Mathematics, Physics)")
    can_add_students = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} (Classes: {self.allowed_levels} | Subjects: {self.subjects_taught})"

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    student_number = models.CharField(max_length=20, unique=True, blank=True, null=True, help_text="Auto-generated unique student ID")
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True, null=True, blank=True)
    level = models.CharField(max_length=50)  # e.g., Senior 1, Senior 2
    
    # Real-World Demographics & History
    date_of_birth = models.DateField(null=True, blank=True)
    student_photo = models.ImageField(upload_to='student_photos/', null=True, blank=True)
    previous_school = models.CharField(max_length=200, null=True, blank=True, help_text="Required if joining Senior 2 or above")
    
    # Parents & Guardians
    mother_name = models.CharField(max_length=150, null=True, blank=True)
    mother_phone = models.CharField(max_length=50, null=True, blank=True)
    father_name = models.CharField(max_length=150, null=True, blank=True)
    father_phone = models.CharField(max_length=50, null=True, blank=True)
    
    guardian_name = models.CharField(max_length=150, null=True, blank=True, help_text="Fill if parents are unavailable")
    guardian_relationship = models.CharField(max_length=50, null=True, blank=True, help_text="e.g., Uncle, Aunt, Grandparent")
    guardian_phone = models.CharField(max_length=50, null=True, blank=True)
    guardian_photo = models.ImageField(upload_to='guardian_photos/', null=True, blank=True)
    
    location = models.CharField(max_length=255, null=True, blank=True, help_text="Home address or residence location")
    
    date_registered = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='registered_students')
    
    is_active = models.BooleanField(default=True, help_text="Uncheck if student has left or withdrawn from school")
    withdrawal_date = models.DateField(null=True, blank=True)
    withdrawal_reason = models.TextField(null=True, blank=True)

    @property
    def age(self):
        """Automatically calculates student age from date of birth."""
        if self.date_of_birth:
            today = datetime.date.today()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None

    def save(self, *args, **kwargs):
        # Auto-generate unique student number if not present (e.g., STU-2026-0001)
        if not self.student_number:
            last_student = Student.objects.all().order_by('id').last()
            next_id = (last_student.id + 1) if last_student else 1
            year = datetime.date.today().year
            self.student_number = f"STU-{year}-{next_id:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        status = "" if self.is_active else " [Withdrawn]"
        return f"[{self.student_number}] {self.name} ({self.level}){status}"


class GradeReport(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades')
    subject = models.CharField(max_length=100)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    term = models.CharField(max_length=50, help_text="e.g., Term 1 2026")
    remarks = models.TextField(blank=True, null=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='recorded_grades')
    date_recorded = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name} - {self.subject}: {self.score} ({self.term})"

class SchoolEvent(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    event_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.event_date}"

class Timetable(models.Model):
    class_level = models.CharField(max_length=50, null=True, blank=True)
    subject = models.CharField(max_length=100, null=True, blank=True)
    day_of_week = models.CharField(max_length=20, null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
