"""Vues : fiches élèves, suivi présences, historique académique"""
import functools
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Avg, Q
from accounts.models import User, StudentProfile, MedicalInfo, AcademicDocument
from .models import Enrollment, Attendance, Schedule, Grade, SubjectGrade, ReportCard, Trimester, Assignment, Classroom
from . import grade_service


def _require_staff(request):
    return request.user.role in ('admin', 'teacher')


@login_required
def student_list(request):
    """Liste de tous les élèves avec filtres"""
    search = request.GET.get('q', '')
    classroom_id = request.GET.get('classroom', '')

    classrooms = Classroom.objects.all()
    students = User.objects.filter(role='student').select_related('student_profile')

    if search:
        students = students.filter(
            Q(first_name__icontains=search) | Q(last_name__icontains=search) |
            Q(email__icontains=search) | Q(student_profile__student_id__icontains=search)
        )
    if classroom_id:
        students = students.filter(
            enrollments__classroom_id=classroom_id, enrollments__is_active=True
        )

    return render(request, 'academic/student_list.html', {
        'students': students, 'classrooms': classrooms,
        'search': search, 'selected_classroom': classroom_id,
    })


@login_required
def student_detail(request, pk):
    """Fiche complète d'un élève"""
    student = get_object_or_404(User, pk=pk, role='student')

    if request.user.role == 'student' and request.user.pk != pk:
        return redirect('dashboard')
    if request.user.role == 'parent':
        if not request.user.children.filter(pk=pk).exists():
            return redirect('dashboard')

    try:
        profile = student.student_profile
    except StudentProfile.DoesNotExist:
        profile = None

    try:
        medical = student.medical_info
    except MedicalInfo.DoesNotExist:
        medical = None

    enrollments = Enrollment.objects.filter(student=student, is_active=True).select_related('classroom__level')
    documents = AcademicDocument.objects.filter(student=student)
    report_cards = ReportCard.objects.filter(student=student).select_related('trimester', 'classroom')

    attendances = Attendance.objects.filter(student=student).order_by('-date')
    att_stats = {
        'total':   attendances.count(),
        'present': attendances.filter(status='present').count(),
        'absent':  attendances.filter(status='absent').count(),
        'late':    attendances.filter(status='late').count(),
        'excused': attendances.filter(status='excused').count(),
    }
    att_stats['rate'] = round(
        att_stats['present'] / att_stats['total'] * 100, 1
    ) if att_stats['total'] > 0 else 100

    recent_grades = Grade.objects.filter(student=student).select_related(
        'assignment__subject').order_by('-graded_at')[:10]

    history = report_cards.order_by('trimester__school_year', 'trimester__number')

    return render(request, 'academic/student_detail.html', {
        'student': student, 'profile': profile, 'medical': medical,
        'enrollments': enrollments, 'documents': documents,
        'report_cards': report_cards, 'att_stats': att_stats,
        'recent_grades': recent_grades, 'attendances': attendances[:20],
        'history': history,
    })


@login_required
def student_attendance_detail(request, pk):
    """Suivi détaillé des présences d'un élève"""
    student = get_object_or_404(User, pk=pk, role='student')
    trimester_id = request.GET.get('trimester', '')
    trimesters = Trimester.objects.all()

    attendances = Attendance.objects.filter(student=student).select_related('schedule__subject').order_by('-date')
    if trimester_id:
        t = get_object_or_404(Trimester, pk=trimester_id)
        attendances = attendances.filter(date__gte=t.start_date, date__lte=t.end_date)

    total = attendances.count()
    stats = {s: attendances.filter(status=s).count() for s in ('present', 'absent', 'late', 'excused')}
    stats['total'] = total
    stats['rate'] = round(stats['present'] / total * 100, 1) if total else 100

    by_subject = {}
    for att in attendances:
        sname = att.schedule.subject.name
        by_subject.setdefault(sname, {'present': 0, 'absent': 0, 'late': 0, 'excused': 0})
        by_subject[sname][att.status] += 1

    return render(request, 'academic/student_attendance.html', {
        'student': student, 'attendances': attendances, 'stats': stats,
        'by_subject': by_subject, 'trimesters': trimesters,
        'selected_trimester': trimester_id,
    })


@login_required
def bulk_attendance(request):
    """Saisie en masse des présences pour une séance"""
    if not _require_staff(request):
        return redirect('dashboard')

    classrooms = Classroom.objects.all()
    schedules  = []
    students   = []
    selected_schedule  = None
    selected_classroom = None

    # Étape 1 : sélection de la classe → charge ses créneaux
    classroom_id = request.GET.get('classroom') or request.POST.get('classroom')
    # Étape 2 : sélection du créneau → charge ses élèves
    schedule_id = request.GET.get('schedule') or request.POST.get('schedule')

    if schedule_id:
        selected_schedule = get_object_or_404(Schedule, pk=schedule_id)
        selected_classroom = selected_schedule.classroom
        students = User.objects.filter(
            enrollments__classroom=selected_schedule.classroom,
            enrollments__is_active=True, role='student'
        ).order_by('last_name', 'first_name')
        schedules = Schedule.objects.filter(
            classroom=selected_schedule.classroom
        ).select_related('subject', 'teacher').order_by('day', 'start_time')

    elif classroom_id:
        # Classe choisie mais pas encore de créneau : charger les créneaux de la classe
        selected_classroom = get_object_or_404(Classroom, pk=classroom_id)
        schedules = Schedule.objects.filter(
            classroom=selected_classroom
        ).select_related('subject', 'teacher').order_by('day', 'start_time')

    if request.method == 'POST' and selected_schedule:
        from datetime import date as date_cls
        att_date = request.POST.get('date') or str(date_cls.today())
        saved = 0
        for student in students:
            status = request.POST.get(f'status_{student.pk}', 'present')
            note   = request.POST.get(f'note_{student.pk}', '')
            Attendance.objects.update_or_create(
                student=student, schedule=selected_schedule, date=att_date,
                defaults={'status': status, 'note': note}
            )
            saved += 1
        messages.success(request, f"Présences enregistrées pour {saved} élève(s).")
        return redirect(f'{request.path}?schedule={schedule_id}')

    return render(request, 'academic/bulk_attendance.html', {
        'classrooms': classrooms, 'schedules': schedules,
        'selected_schedule': selected_schedule,
        'selected_classroom': selected_classroom,
        'students': students,
    })


@login_required
def medical_edit(request, pk):
    """Redirige vers la vue médicale unifiée (accounts)."""
    return redirect('medical_edit_for', pk=pk)


@login_required
def document_upload(request, pk):
    if not _require_staff(request):
        return redirect('dashboard')
    student = get_object_or_404(User, pk=pk, role='student')

    if request.method == 'POST':
        AcademicDocument.objects.create(
            student=student,
            title=request.POST.get('title', ''),
            doc_type=request.POST.get('doc_type', 'other'),
            school_year=request.POST.get('school_year', ''),
            notes=request.POST.get('notes', ''),
            file=request.FILES.get('file'),
        )
        messages.success(request, "Document ajouté.")
        return redirect('student_detail', pk=pk)

    return render(request, 'academic/document_upload.html', {'student': student})
