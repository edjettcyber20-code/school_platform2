from django import forms
from accounts.models import User
from .models import (Classroom, Subject, Level, Schedule, Assignment,
                     Grade, Attendance, Announcement, Enrollment)


class LevelForm(forms.ModelForm):
    class Meta:
        model = Level
        fields = ['name', 'order']
        widgets = {
            'name':  forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex : 6ème, 5ème, Terminale…'}),
            'order': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '1, 2, 3…'}),
        }
        labels = {'name': 'Nom du niveau', 'order': 'Ordre d\'affichage'}


class ClassroomForm(forms.ModelForm):
    class Meta:
        model = Classroom
        fields = ['name', 'level', 'capacity', 'school_year', 'teachers', 'subjects']
        widgets = {
            'teachers': forms.CheckboxSelectMultiple(),
            'subjects': forms.CheckboxSelectMultiple(),
        }


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code', 'coefficient', 'color']


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['classroom', 'subject', 'teacher', 'day', 'start_time', 'end_time', 'room']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time':   forms.TimeInput(attrs={'type': 'time'}),
        }


class AssignmentForm(forms.ModelForm):
    teacher = forms.ModelChoiceField(
        queryset=User.objects.filter(role='teacher').order_by('last_name', 'first_name'),
        label='Enseignant responsable',
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = Assignment
        fields = ['title', 'description', 'type', 'subject', 'classroom', 'teacher', 'due_date', 'max_score']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['student', 'assignment', 'score', 'comment']


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['student', 'schedule', 'date', 'status', 'note']
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'target_role', 'is_pinned']


class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['student', 'classroom']
