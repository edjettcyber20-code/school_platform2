import functools
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count
from accounts.models import User
from .models import (Classroom, Subject, Level, Schedule, Assignment,
                     Grade, Attendance, Announcement, Enrollment)
from .forms import (ClassroomForm, SubjectForm, ScheduleForm, AssignmentForm,
                    GradeForm, AttendanceForm, AnnouncementForm, EnrollmentForm,
                    LevelForm)


def admin_required(view_func):
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'admin':
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def teacher_or_admin(view_func):
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role not in ['admin', 'teacher']:
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


# ══════════════════════════════════════════════════════════════════════════════
# NIVEAUX (Level)
# ══════════════════════════════════════════════════════════════════════════════
@login_required
def level_list(request):
    levels = Level.objects.prefetch_related('classrooms').all()
    return render(request, 'academic/level_list.html', {'levels': levels})


@login_required
@admin_required
def level_create(request):
    form = LevelForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Niveau créé avec succès.")
        return redirect('level_list')
    return render(request, 'academic/level_form.html', {
        'form': form, 'title': 'Créer un niveau', 'back_url': 'level_list'
    })


@login_required
@admin_required
def level_edit(request, pk):
    level = get_object_or_404(Level, pk=pk)
    form = LevelForm(request.POST or None, instance=level)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f"Niveau « {level.name} » modifié.")
        return redirect('level_list')
    return render(request, 'academic/level_form.html', {
        'form': form, 'title': f'Modifier — {level.name}',
        'back_url': 'level_list', 'level': level
    })


@login_required
@admin_required
def level_delete(request, pk):
    level = get_object_or_404(Level, pk=pk)
    if request.method == 'POST':
        nb = level.classrooms.count()
        if nb > 0:
            messages.error(request, f"Impossible de supprimer : {nb} classe(s) utilisent ce niveau.")
        else:
            name = level.name
            level.delete()
            messages.success(request, f"Niveau « {name} » supprimé.")
        return redirect('level_list')
    return render(request, 'academic/level_confirm_delete.html', {'level': level})


# ══════════════════════════════════════════════════════════════════════════════
# CLASSES
# ══════════════════════════════════════════════════════════════════════════════
@login_required
def classroom_list(request):
    if request.user.role == 'teacher':
        classrooms = request.user.classrooms.all()
    else:
        classrooms = Classroom.objects.select_related('level').all()
    return render(request, 'academic/classroom_list.html', {'classrooms': classrooms})


@login_required
@admin_required
def classroom_create(request):
    form = ClassroomForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Classe créée avec succès.")
        return redirect('classroom_list')
    return render(request, 'academic/form.html', {
        'form': form, 'title': 'Créer une classe', 'back_url': 'classroom_list'
    })


@login_required
@admin_required
def classroom_edit(request, pk):
    classroom = get_object_or_404(Classroom, pk=pk)
    form = ClassroomForm(request.POST or None, instance=classroom)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Classe modifiée.")
        return redirect('classroom_list')
    return render(request, 'academic/form.html', {
        'form': form, 'title': 'Modifier la classe', 'back_url': 'classroom_list'
    })


@login_required
def classroom_detail(request, pk):
    classroom = get_object_or_404(Classroom, pk=pk)
    students = User.objects.filter(enrollments__classroom=classroom, enrollments__is_active=True)
    schedules = classroom.schedules.select_related('subject', 'teacher').order_by('day', 'start_time')
    assignments = classroom.assignments.order_by('-created_at')[:10]
    return render(request, 'academic/classroom_detail.html', {
        'classroom': classroom, 'students': students,
        'schedules': schedules, 'assignments': assignments
    })


# ══════════════════════════════════════════════════════════════════════════════
# MATIÈRES
# ══════════════════════════════════════════════════════════════════════════════
@login_required
def subject_list(request):
    subjects = Subject.objects.all()
    return render(request, 'academic/subject_list.html', {'subjects': subjects})


@login_required
@admin_required
def subject_create(request):
    form = SubjectForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Matière créée.")
        return redirect('subject_list')
    return render(request, 'academic/form.html', {
        'form': form, 'title': 'Créer une matière', 'back_url': 'subject_list'
    })


# ══════════════════════════════════════════════════════════════════════════════
# EMPLOI DU TEMPS
# ══════════════════════════════════════════════════════════════════════════════
@login_required
def schedule_view(request):
    classroom_id = request.GET.get('classroom')
    classrooms = Classroom.objects.all()
    schedules = []
    selected_classroom = None

    if classroom_id:
        selected_classroom = get_object_or_404(Classroom, pk=classroom_id)
        schedules = selected_classroom.schedules.select_related('subject', 'teacher').order_by('day', 'start_time')
    elif request.user.role == 'student':
        enrollment = request.user.enrollments.filter(is_active=True).first()
        if enrollment:
            selected_classroom = enrollment.classroom
            schedules = selected_classroom.schedules.select_related('subject', 'teacher').order_by('day', 'start_time')
    elif request.user.role == 'teacher':
        schedules = Schedule.objects.filter(teacher=request.user).select_related('subject', 'classroom').order_by('day', 'start_time')

    days_order = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
    days_labels = {
        'monday': 'Lundi', 'tuesday': 'Mardi', 'wednesday': 'Mercredi',
        'thursday': 'Jeudi', 'friday': 'Vendredi', 'saturday': 'Samedi'
    }
    schedule_by_day = {d: [] for d in days_order}
    for s in schedules:
        if s.day in schedule_by_day:
            schedule_by_day[s.day].append(s)

    return render(request, 'academic/schedule.html', {
        'classrooms': classrooms, 'selected_classroom': selected_classroom,
        'schedule_by_day': schedule_by_day,
        'days_order': days_order, 'days_labels': days_labels,
    })


@login_required
@admin_required
def schedule_create(request):
    form = ScheduleForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Créneau ajouté.")
        return redirect('schedule_view')
    return render(request, 'academic/form.html', {
        'form': form, 'title': "Ajouter un créneau", 'back_url': 'schedule_view'
    })


# ══════════════════════════════════════════════════════════════════════════════
# DEVOIRS & EXAMENS
# ══════════════════════════════════════════════════════════════════════════════
@login_required
def assignment_list(request):
    if request.user.role == 'teacher':
        assignments = Assignment.objects.filter(teacher=request.user).order_by('-created_at')
    elif request.user.role == 'student':
        assignments = Assignment.objects.filter(
            classroom__enrollments__student=request.user,
            classroom__enrollments__is_active=True
        ).order_by('due_date')
    else:
        assignments = Assignment.objects.all().order_by('-created_at')
    return render(request, 'academic/assignment_list.html', {'assignments': assignments})


@login_required
@teacher_or_admin
def assignment_create(request):
    form = AssignmentForm(request.POST or None)
    if request.user.role == 'teacher':
        form.fields['teacher'].required = False
        form.fields['teacher'].widget = form.fields['teacher'].hidden_widget()

    if request.method == 'POST' and form.is_valid():
        a = form.save(commit=False)
        if request.user.role == 'teacher':
            a.teacher = request.user
        elif not a.teacher_id:
            messages.error(request, "Veuillez sélectionner un enseignant responsable.")
            return render(request, 'academic/form.html', {
                'form': form, 'title': 'Créer un devoir/examen', 'back_url': 'assignment_list'
            })
        a.save()
        messages.success(request, "Devoir créé.")
        return redirect('assignment_list')

    return render(request, 'academic/form.html', {
        'form': form, 'title': 'Créer un devoir/examen', 'back_url': 'assignment_list'
    })


# ══════════════════════════════════════════════════════════════════════════════
# NOTES
# ══════════════════════════════════════════════════════════════════════════════
@login_required
def grade_list(request):
    if request.user.role == 'student':
        grades = Grade.objects.filter(student=request.user).select_related('assignment__subject').order_by('-graded_at')
        avg = grades.aggregate(Avg('score'))['score__avg']
        return render(request, 'academic/grade_list.html', {'grades': grades, 'avg': avg})
    elif request.user.role == 'teacher':
        assignments = Assignment.objects.filter(teacher=request.user)
        return render(request, 'academic/grade_list.html', {'assignments': assignments})
    else:
        grades = Grade.objects.all().select_related('student', 'assignment__subject').order_by('-graded_at')
        return render(request, 'academic/grade_list.html', {'grades': grades})


@login_required
@teacher_or_admin
def grade_create(request):
    form = GradeForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Note enregistrée.")
        return redirect('grade_list')
    return render(request, 'academic/form.html', {
        'form': form, 'title': 'Saisir une note', 'back_url': 'grade_list'
    })


# ══════════════════════════════════════════════════════════════════════════════
# PRÉSENCES
# ══════════════════════════════════════════════════════════════════════════════
@login_required
def attendance_list(request):
    if request.user.role == 'student':
        attendances = Attendance.objects.filter(student=request.user).order_by('-date')
        total = attendances.count()
        absences = attendances.filter(status='absent').count()
        return render(request, 'academic/attendance_list.html', {
            'attendances': attendances, 'total': total, 'absences': absences
        })
    attendances = Attendance.objects.all().select_related('student', 'schedule__subject').order_by('-date')
    return render(request, 'academic/attendance_list.html', {'attendances': attendances})


@login_required
@teacher_or_admin
def attendance_create(request):
    form = AttendanceForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Présence enregistrée.")
        return redirect('attendance_list')
    return render(request, 'academic/form.html', {
        'form': form, 'title': 'Enregistrer une présence', 'back_url': 'attendance_list'
    })


# ══════════════════════════════════════════════════════════════════════════════
# ANNONCES
# ══════════════════════════════════════════════════════════════════════════════
@login_required
def announcement_list(request):
    role = request.user.role
    announcements = Announcement.objects.filter(target_role__in=['all', role]).order_by('-is_pinned', '-created_at')
    return render(request, 'academic/announcement_list.html', {'announcements': announcements})


@login_required
@admin_required
def announcement_create(request):
    form = AnnouncementForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        a = form.save(commit=False)
        a.author = request.user
        a.save()
        messages.success(request, "Annonce publiée.")
        return redirect('announcement_list')
    return render(request, 'academic/form.html', {
        'form': form, 'title': 'Nouvelle annonce', 'back_url': 'announcement_list'
    })


# ══════════════════════════════════════════════════════════════════════════════
# INSCRIPTIONS
# ══════════════════════════════════════════════════════════════════════════════
@login_required
@admin_required
def enrollment_create(request):
    form = EnrollmentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Élève inscrit avec succès.")
        return redirect('classroom_list')
    return render(request, 'academic/form.html', {
        'form': form, 'title': "Inscrire un élève", 'back_url': 'classroom_list'
    })
