from django import forms
from .models import Student,SchoolEvent
from .models import GradeReport, Student

from django import forms
from .models import Student, SchoolEvent, GradeReport

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'name', 
            'level', 
            'date_of_birth', 
            'student_photo', 
            'previous_school', 
            'mother_name', 
            'mother_phone', 
            'father_name', 
            'father_phone', 
            'guardian_name', 
            'guardian_relationship', 
            'guardian_phone', 
            'guardian_photo', 
            'location', 
            'email'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'level': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Senior 1, Senior 2'}),
            'previous_school': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Previous school (if applicable)'}),
            'mother_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Mother's Full Name"}),
            'mother_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Mother's Phone Number"}),
            'father_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Father's Full Name"}),
            'father_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Father's Phone Number"}),
            'guardian_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Guardian Name (if parents unavailable)'}),
            'guardian_relationship': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Aunt, Uncle, Grandparent'}),
            'guardian_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Guardian Phone Number'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Home Address / Location'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'student@example.com'}),
        }

class StudentWithdrawalForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['withdrawal_reason']
        widgets = {
            'withdrawal_reason': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Provide a reason for student withdrawal...'}),
        }

class SchoolEventForm(forms.ModelForm):
    class Meta:
        model = SchoolEvent
        fields = ['title', 'description', 'event_date']
        widgets = {
            'event_date': forms.DateInput(attrs={'type': 'date'}),
        }

class GradeReportForm(forms.ModelForm):
    class Meta:
        model = GradeReport
        fields = ['subject', 'score', 'term', 'remarks']