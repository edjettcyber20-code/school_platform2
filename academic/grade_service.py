"""
Service de calcul automatique des moyennes et classements
"""
from decimal import Decimal, ROUND_HALF_UP
from django.db.models import Avg, Min, Max
from .models import Grade, SubjectGrade, ReportCard, Trimester, Classroom, Subject
from accounts.models import User


def compute_subject_average(student, subject, classroom, trimester):
    """Calcule et sauvegarde la moyenne d'un élève dans une matière pour un trimestre."""
    grades = Grade.objects.filter(
        student=student,
        assignment__subject=subject,
        assignment__classroom=classroom,
        assignment__due_date__date__gte=trimester.start_date,
        assignment__due_date__date__lte=trimester.end_date,
    )
    if not grades.exists():
        return None

    total_pts = Decimal('0')
    count = 0
    for g in grades:
        normalized = (Decimal(str(g.score)) / Decimal(str(g.assignment.max_score))) * Decimal('20')
        total_pts += normalized
        count += 1

    avg = (total_pts / count).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    weighted = (avg * subject.coefficient).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    sg, _ = SubjectGrade.objects.get_or_create(
        student=student, subject=subject,
        classroom=classroom, trimester=trimester
    )
    sg.average = avg
    sg.weighted_average = weighted
    sg.save(update_fields=['average', 'weighted_average', 'updated_at'])
    return avg


def compute_student_general_average(student, classroom, trimester):
    """Calcule la moyenne générale d'un élève sur un trimestre."""
    # Recalculate all subject grades first
    for subject in classroom.subjects.all():
        compute_subject_average(student, subject, classroom, trimester)

    sgs = SubjectGrade.objects.filter(
        student=student, classroom=classroom, trimester=trimester,
        average__isnull=False
    )
    if not sgs.exists():
        return None

    total_weighted = sum(sg.average * sg.subject.coefficient for sg in sgs)
    total_coeff    = sum(sg.subject.coefficient for sg in sgs)
    if total_coeff == 0:
        return None

    general_avg = (total_weighted / total_coeff).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return general_avg


def compute_class_rankings(classroom, trimester):
    """
    Calcule et sauvegarde les moyennes + rangs pour tous les élèves d'une classe.
    Retourne la liste triée des (student, average).
    """
    from accounts.models import User
    from .models import Attendance

    students = User.objects.filter(
        enrollments__classroom=classroom,
        enrollments__is_active=True,
        role='student'
    )

    averages = []
    for student in students:
        avg = compute_student_general_average(student, classroom, trimester)
        if avg is not None:
            averages.append((student, avg))

    # Sort descending
    averages.sort(key=lambda x: x[1], reverse=True)

    class_avgs = [a for _, a in averages]
    class_avg  = (sum(class_avgs) / len(class_avgs)).quantize(Decimal('0.01')) if class_avgs else None
    highest    = max(class_avgs) if class_avgs else None
    lowest     = min(class_avgs) if class_avgs else None

    for rank, (student, avg) in enumerate(averages, start=1):
        rc, _ = ReportCard.objects.get_or_create(
            student=student, classroom=classroom, trimester=trimester
        )
        rc.general_average = avg
        rc.rank            = rank
        rc.class_size      = len(averages)
        rc.class_average   = class_avg
        rc.highest_average = highest
        rc.lowest_average  = lowest

        # Attendance
        from .models import Attendance
        atts = Attendance.objects.filter(
            student=student,
            date__gte=trimester.start_date,
            date__lte=trimester.end_date
        )
        rc.absences_total    = atts.filter(status='absent').count()
        rc.absences_justified= atts.filter(status='excused').count()
        rc.lates_total       = atts.filter(status='late').count()
        rc.save()

    return averages


def get_student_ranking_detail(student, classroom, trimester):
    """Retourne les détails de classement pour un élève."""
    try:
        rc = ReportCard.objects.get(student=student, classroom=classroom, trimester=trimester)
        return rc
    except ReportCard.DoesNotExist:
        return None


def get_subject_stats(subject, classroom, trimester):
    """Stats globales d'une matière dans une classe sur un trimestre."""
    sgs = SubjectGrade.objects.filter(
        subject=subject, classroom=classroom, trimester=trimester,
        average__isnull=False
    )
    if not sgs.exists():
        return None
    avgs = [float(sg.average) for sg in sgs]
    return {
        'count': len(avgs),
        'avg': round(sum(avgs) / len(avgs), 2),
        'highest': max(avgs),
        'lowest': min(avgs),
        'above_10': sum(1 for a in avgs if a >= 10),
        'below_10': sum(1 for a in avgs if a < 10),
    }
