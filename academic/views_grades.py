"""Vues : gestion avancée des notes, bulletins, classement"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.db.models import Q
from accounts.models import User
from .models import (Grade, Assignment, SubjectGrade, ReportCard,
                     Trimester, Classroom, Subject, Enrollment)
from . import grade_service


# ── TRIMESTRE ─────────────────────────────────────────────────────────────────
@login_required
def trimester_list(request):
    if request.user.role != 'admin':
        return redirect('dashboard')
    trimesters = Trimester.objects.all()
    return render(request, 'academic/trimester_list.html', {'trimesters': trimesters})


@login_required
def trimester_create(request):
    if request.user.role != 'admin':
        return redirect('dashboard')
    if request.method == 'POST':
        Trimester.objects.create(
            school_year=request.POST['school_year'],
            number=request.POST['number'],
            start_date=request.POST['start_date'],
            end_date=request.POST['end_date'],
            is_active='is_active' in request.POST,
        )
        messages.success(request, "Trimestre créé.")
        return redirect('trimester_list')
    return render(request, 'academic/trimester_form.html', {'title': 'Créer un trimestre'})


# ── SAISIE NOTES PAR DEVOIR ───────────────────────────────────────────────────
@login_required
def grade_entry(request, assignment_id):
    """Saisie des notes pour tous les élèves d'un devoir"""
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    if request.user.role == 'teacher' and assignment.teacher != request.user:
        messages.error(request, "Accès refusé.")
        return redirect('assignment_list')

    students = User.objects.filter(
        enrollments__classroom=assignment.classroom,
        enrollments__is_active=True, role='student'
    ).order_by('last_name', 'first_name')

    existing = {g.student_id: g for g in Grade.objects.filter(assignment=assignment)}

    if request.method == 'POST':
        saved = 0
        for student in students:
            score_str = request.POST.get(f'score_{student.pk}', '').strip()
            comment   = request.POST.get(f'comment_{student.pk}', '').strip()
            if score_str:
                try:
                    score = float(score_str)
                    if 0 <= score <= float(assignment.max_score):
                        Grade.objects.update_or_create(
                            student=student, assignment=assignment,
                            defaults={'score': score, 'comment': comment}
                        )
                        saved += 1
                except ValueError:
                    pass
        messages.success(request, f"{saved} note(s) enregistrée(s).")
        return redirect('grade_entry', assignment_id=assignment_id)

    rows = []
    for st in students:
        g = existing.get(st.pk)
        rows.append({'student': st, 'grade': g})

    return render(request, 'academic/grade_entry.html', {
        'assignment': assignment, 'rows': rows,
        'graded_count': len([r for r in rows if r['grade']]),
    })


# ── TABLEAU DES NOTES PAR CLASSE ─────────────────────────────────────────────
@login_required
def grade_matrix(request):
    """Vue matricielle : élèves × matières"""
    classroom_id  = request.GET.get('classroom')
    trimester_id  = request.GET.get('trimester')
    classrooms    = Classroom.objects.all()
    trimesters    = Trimester.objects.all()

    matrix = []
    subjects = []
    students = []
    selected_classroom = None
    selected_trimester = None

    if classroom_id and trimester_id:
        selected_classroom = get_object_or_404(Classroom, pk=classroom_id)
        selected_trimester = get_object_or_404(Trimester, pk=trimester_id)
        subjects  = selected_classroom.subjects.all().order_by('name')
        students  = User.objects.filter(
            enrollments__classroom=selected_classroom,
            enrollments__is_active=True, role='student'
        ).order_by('last_name', 'first_name')

        sg_map = {}
        for sg in SubjectGrade.objects.filter(
            classroom=selected_classroom, trimester=selected_trimester,
            student__in=students
        ).select_related('subject', 'student'):
            sg_map[(sg.student_id, sg.subject_id)] = sg

        for student in students:
            row = {'student': student, 'grades': []}
            gen_avg = None
            rank = None
            try:
                rc = ReportCard.objects.get(
                    student=student, classroom=selected_classroom,
                    trimester=selected_trimester
                )
                gen_avg = rc.general_average
                rank    = rc.rank
            except ReportCard.DoesNotExist:
                pass

            for subj in subjects:
                sg = sg_map.get((student.pk, subj.pk))
                row['grades'].append(sg)
            row['general_average'] = gen_avg
            row['rank'] = rank
            matrix.append(row)

        matrix.sort(key=lambda r: float(r['general_average'] or 0), reverse=True)

    return render(request, 'academic/grade_matrix.html', {
        'classrooms': classrooms, 'trimesters': trimesters,
        'selected_classroom': selected_classroom, 'selected_trimester': selected_trimester,
        'subjects': subjects, 'matrix': matrix,
    })


# ── CALCUL AUTOMATIQUE DES MOYENNES ──────────────────────────────────────────
@login_required
def compute_averages(request):
    if request.user.role not in ('admin', 'teacher'):
        return redirect('dashboard')

    classroom_id  = request.POST.get('classroom') or request.GET.get('classroom')
    trimester_id  = request.POST.get('trimester') or request.GET.get('trimester')

    if not classroom_id or not trimester_id:
        messages.error(request, "Classe et trimestre requis.")
        return redirect('grade_matrix')

    classroom = get_object_or_404(Classroom, pk=classroom_id)
    trimester = get_object_or_404(Trimester, pk=trimester_id)

    rankings = grade_service.compute_class_rankings(classroom, trimester)
    messages.success(request, f"Moyennes calculées pour {len(rankings)} élève(s). Classement mis à jour.")

    # URL construite proprement avec reverse()
    base = reverse('grade_matrix')
    return redirect(f'{base}?classroom={classroom_id}&trimester={trimester_id}')


# ── BULLETIN PDF ──────────────────────────────────────────────────────────────
@login_required
def report_card_detail(request, pk):
    rc = get_object_or_404(ReportCard, pk=pk)

    if request.user.role == 'student' and rc.student != request.user:
        return redirect('dashboard')
    if request.user.role == 'parent' and not request.user.children.filter(pk=rc.student_id).exists():
        return redirect('dashboard')

    sgs = SubjectGrade.objects.filter(
        student=rc.student, classroom=rc.classroom, trimester=rc.trimester
    ).select_related('subject').order_by('subject__name')

    return render(request, 'academic/report_card_detail.html', {'rc': rc, 'sgs': sgs})


@login_required
def report_card_pdf(request, pk):
    """Génère et retourne le bulletin PDF"""
    rc = get_object_or_404(ReportCard, pk=pk)

    if request.user.role == 'student' and rc.student != request.user:
        return redirect('dashboard')
    if request.user.role == 'parent' and not request.user.children.filter(pk=rc.student_id).exists():
        return redirect('dashboard')

    from .pdf_generator import generate_report_card_pdf
    buf = generate_report_card_pdf(rc)

    student_name = rc.student.get_full_name().replace(' ', '_')
    filename = f"bulletin_{student_name}_T{rc.trimester.number}_{rc.trimester.school_year}.pdf"

    response = HttpResponse(buf.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
def report_card_preview(request, pk):
    """Prévisualise le bulletin en ligne"""
    rc = get_object_or_404(ReportCard, pk=pk)

    if request.user.role == 'student' and rc.student != request.user:
        return redirect('dashboard')
    if request.user.role == 'parent' and not request.user.children.filter(pk=rc.student_id).exists():
        return redirect('dashboard')

    from .pdf_generator import generate_report_card_pdf
    buf = generate_report_card_pdf(rc)
    response = HttpResponse(buf.read(), content_type='application/pdf')
    response['Content-Disposition'] = 'inline'
    return response


@login_required
def report_card_list(request):
    """Liste des bulletins disponibles"""
    if request.user.role == 'student':
        rcs = ReportCard.objects.filter(student=request.user).select_related('trimester', 'classroom')
    elif request.user.role == 'parent':
        rcs = ReportCard.objects.filter(
            student__in=request.user.children.all()
        ).select_related('trimester', 'classroom', 'student')
    elif request.user.role == 'teacher':
        rcs = ReportCard.objects.filter(
            classroom__in=request.user.classrooms.all()
        ).select_related('trimester', 'classroom', 'student')
    else:
        classroom_id = request.GET.get('classroom')
        trimester_id = request.GET.get('trimester')
        rcs = ReportCard.objects.all().select_related('trimester', 'classroom', 'student')
        if classroom_id:
            rcs = rcs.filter(classroom_id=classroom_id)
        if trimester_id:
            rcs = rcs.filter(trimester_id=trimester_id)

    classrooms = Classroom.objects.all()
    trimesters = Trimester.objects.all()

    return render(request, 'academic/report_card_list.html', {
        'rcs': rcs, 'classrooms': classrooms, 'trimesters': trimesters,
    })


@login_required
def report_card_edit(request, pk):
    """Édition manuelle d'un bulletin (commentaires, conduite)"""
    if request.user.role not in ('admin', 'teacher'):
        return redirect('dashboard')
    rc = get_object_or_404(ReportCard, pk=pk)

    if request.method == 'POST':
        rc.class_teacher_comment = request.POST.get('class_teacher_comment', '')
        rc.principal_comment     = request.POST.get('principal_comment', '')
        rc.conduct_grade         = request.POST.get('conduct_grade', 'B')
        rc.status                = request.POST.get('status', 'draft')
        rc.save()
        messages.success(request, "Bulletin mis à jour.")
        return redirect('report_card_detail', pk=pk)

    sgs = SubjectGrade.objects.filter(
        student=rc.student, classroom=rc.classroom, trimester=rc.trimester
    ).select_related('subject')

    return render(request, 'academic/report_card_edit.html', {'rc': rc, 'sgs': sgs})


@login_required
def subject_grade_comment(request, pk):
    """Mise à jour du commentaire enseignant sur une note de matière"""
    sg = get_object_or_404(SubjectGrade, pk=pk)
    if request.method == 'POST':
        sg.teacher_comment = request.POST.get('comment', '')
        sg.save(update_fields=['teacher_comment', 'updated_at'])
        messages.success(request, "Commentaire sauvegardé.")
    next_url = request.POST.get('next', '')
    return redirect(next_url if next_url else reverse('grade_matrix'))


# ── CLASSEMENT ────────────────────────────────────────────────────────────────
@login_required
def class_ranking(request):
    """Tableau de classement d'une classe sur un trimestre"""
    classroom_id = request.GET.get('classroom')
    trimester_id = request.GET.get('trimester')
    classrooms   = Classroom.objects.all()
    trimesters   = Trimester.objects.all()
    rankings     = []
    selected_classroom = None
    selected_trimester = None

    if classroom_id and trimester_id:
        selected_classroom = get_object_or_404(Classroom, pk=classroom_id)
        selected_trimester = get_object_or_404(Trimester, pk=trimester_id)
        rcs = ReportCard.objects.filter(
            classroom=selected_classroom, trimester=selected_trimester,
            general_average__isnull=False
        ).select_related('student').order_by('rank')
        rankings = rcs

    return render(request, 'academic/class_ranking.html', {
        'classrooms': classrooms, 'trimesters': trimesters,
        'selected_classroom': selected_classroom,
        'selected_trimester': selected_trimester,
        'rankings': rankings,
    })


# ── GÉNÉRATION BULLETINS EN LOT ──────────────────────────────────────────────
@login_required
def generate_all_reports(request):
    """Génère tous les bulletins PDF d'une classe en une fois"""
    if request.user.role != 'admin':
        return redirect('dashboard')

    classroom_id = request.POST.get('classroom')
    trimester_id = request.POST.get('trimester')

    if not classroom_id or not trimester_id:
        messages.error(request, "Paramètres manquants.")
        return redirect('report_card_list')

    classroom = get_object_or_404(Classroom, pk=classroom_id)
    trimester = get_object_or_404(Trimester, pk=trimester_id)

    grade_service.compute_class_rankings(classroom, trimester)

    rcs = ReportCard.objects.filter(classroom=classroom, trimester=trimester)
    count = rcs.count()

    messages.success(request, f"{count} bulletin(s) recalculé(s) pour {classroom.name} - {trimester}.")

    # URL propre via reverse()
    base = reverse('report_card_list')
    return redirect(f'{base}?classroom={classroom_id}&trimester={trimester_id}')
