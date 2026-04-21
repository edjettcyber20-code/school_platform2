"""
Données supplémentaires : trimestres, notes complètes, présences, bulletins
"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_platform.settings')
django.setup()

from datetime import date, timedelta
from decimal import Decimal
from django.utils import timezone
from accounts.models import User, MedicalInfo, StudentProfile
from academic.models import (
    Trimester, Classroom, Subject, Assignment, Grade,
    Schedule, Attendance, SubjectGrade, ReportCard, Enrollment
)
from academic import grade_service

print("Création des trimestres...")
t1, _ = Trimester.objects.get_or_create(school_year='2024-2025', number='1', defaults={
    'start_date': date(2024, 9, 2), 'end_date': date(2024, 11, 30), 'is_active': False
})
t2, _ = Trimester.objects.get_or_create(school_year='2024-2025', number='2', defaults={
    'start_date': date(2024, 12, 2), 'end_date': date(2025, 3, 15), 'is_active': True
})
t3, _ = Trimester.objects.get_or_create(school_year='2024-2025', number='3', defaults={
    'start_date': date(2025, 3, 17), 'end_date': date(2025, 6, 28), 'is_active': False
})

cls1 = Classroom.objects.get(name='6ème A')
cls2 = Classroom.objects.get(name='5ème B')

students_cls1 = list(User.objects.filter(
    role='student', enrollments__classroom=cls1, enrollments__is_active=True
).order_by('last_name'))
students_cls2 = list(User.objects.filter(
    role='student', enrollments__classroom=cls2, enrollments__is_active=True
).order_by('last_name'))

maths   = Subject.objects.get(code='MATH')
french  = Subject.objects.get(code='FRAN')
svt     = Subject.objects.get(code='SVT')
histoire= Subject.objects.get(code='HG')
anglais = Subject.objects.get(code='ANG')
physique= Subject.objects.get(code='PHY')

t1_teacher = User.objects.get(username='prof1')
t2_teacher = User.objects.get(username='prof2')
t3_teacher = User.objects.get(username='prof3')

print("Création des devoirs complets pour T1...")

def make_assignment(title, atype, subject, classroom, teacher, due_date, max_score=20):
    return Assignment.objects.get_or_create(
        title=title, subject=subject, classroom=classroom,
        defaults=dict(type=atype, teacher=teacher, due_date=timezone.make_aware(
            timezone.datetime.combine(due_date, timezone.datetime.min.time())),
            max_score=max_score, description=f"Évaluation de {subject.name}")
    )[0]

# 6ème A — T1
a_math1   = make_assignment("Contrôle N°1 - Nombres entiers", 'exam', maths,  cls1, t1_teacher, date(2024,10,15))
a_math2   = make_assignment("Devoir maison - Fractions",     'homework', maths,   cls1, t1_teacher, date(2024,11,5))
a_math3   = make_assignment("Interro - Tableaux",            'quiz', maths,   cls1, t1_teacher, date(2024,11,20))
a_fr1     = make_assignment("Rédaction - La rentrée",        'exam', french,  cls1, t2_teacher, date(2024,10,20))
a_fr2     = make_assignment("Dictée n°1",                    'quiz', french,  cls1, t2_teacher, date(2024,11,10))
a_svt1    = make_assignment("Contrôle - La cellule",         'exam', svt,     cls1, t3_teacher, date(2024,10,25))
a_hist1   = make_assignment("Contrôle - Préhistoire",        'exam', histoire,cls1, t2_teacher, date(2024,11,15))
a_ang1    = make_assignment("Test vocabulaire",              'quiz', anglais, cls1, t2_teacher, date(2024,11,18))

# Scores réalistes par élève (6ème A, 6 élèves)
scores_t1 = {
    # (math1, math2, math3, fr1, fr2, svt1, hist1, ang1)
    0: [16,17,15, 14,15, 13, 12,14],  # Kofi      – bon élève
    1: [12,13,11, 16,17, 14, 15,13],  # Adjoa     – fort en lettres
    2: [9, 10, 8, 10,11,  9, 11,10],  # Yao       – passable
    3: [18,19,17, 15,16, 17, 16,15],  # Akosua    – excellent
    4: [7,  8, 6,  9, 8,  8,  9, 7],  # Kwame     – en difficulté
    5: [14,14,13, 13,14, 12, 14,13],  # Abena     – correct
}

print("Saisie des notes T1 pour 6ème A...")
for idx, student in enumerate(students_cls1):
    sc = scores_t1.get(idx, [10]*8)
    Grade.objects.get_or_create(student=student, assignment=a_math1,  defaults={'score': sc[0], 'comment': ''})
    Grade.objects.get_or_create(student=student, assignment=a_math2,  defaults={'score': sc[1], 'comment': ''})
    Grade.objects.get_or_create(student=student, assignment=a_math3,  defaults={'score': sc[2], 'comment': ''})
    Grade.objects.get_or_create(student=student, assignment=a_fr1,    defaults={'score': sc[3], 'comment': ''})
    Grade.objects.get_or_create(student=student, assignment=a_fr2,    defaults={'score': sc[4], 'comment': ''})
    Grade.objects.get_or_create(student=student, assignment=a_svt1,   defaults={'score': sc[5], 'comment': ''})
    Grade.objects.get_or_create(student=student, assignment=a_hist1,  defaults={'score': sc[6], 'comment': ''})
    Grade.objects.get_or_create(student=student, assignment=a_ang1,   defaults={'score': sc[7], 'comment': ''})

# 5ème B — T1
a_math_b1  = make_assignment("Contrôle - Équations",    'exam', maths,   cls2, t1_teacher, date(2024,10,18))
a_phys_b1  = make_assignment("TP - Mesures",            'exam', physique,cls2, t3_teacher, date(2024,10,22))
a_svt_b1   = make_assignment("Contrôle - Nutrition",    'exam', svt,     cls2, t3_teacher, date(2024,11,12))
a_ang_b1   = make_assignment("Oral anglais",            'quiz', anglais, cls2, t2_teacher, date(2024,11,14))

scores_b_t1 = {
    0: [15,13,14,12], 1: [11,10,12,13], 2: [17,16,15,14], 3: [8,9,7,10]
}
for idx, student in enumerate(students_cls2):
    sc = scores_b_t1.get(idx, [10]*4)
    Grade.objects.get_or_create(student=student, assignment=a_math_b1, defaults={'score': sc[0]})
    Grade.objects.get_or_create(student=student, assignment=a_phys_b1, defaults={'score': sc[1]})
    Grade.objects.get_or_create(student=student, assignment=a_svt_b1,  defaults={'score': sc[2]})
    Grade.objects.get_or_create(student=student, assignment=a_ang_b1,  defaults={'score': sc[3]})

print("Présences réalistes T1...")
sched_list = list(Schedule.objects.filter(classroom=cls1)[:3])
absence_map = {0: [], 1: [1], 2: [0,2], 3: [], 4: [0,1,2], 5: [1]}
if sched_list:
    for day_offset in range(0, 60, 7):
        att_date = t1.start_date + timedelta(days=day_offset)
        for s_idx, sched in enumerate(sched_list):
            for st_idx, student in enumerate(students_cls1):
                status = 'absent' if s_idx in absence_map.get(st_idx, []) and day_offset < 30 else 'present'
                Attendance.objects.get_or_create(
                    student=student, schedule=sched, date=att_date,
                    defaults={'status': status, 'note': 'Non justifiée' if status == 'absent' else ''}
                )

print("Calcul des moyennes et classements T1 — 6ème A...")
rankings_1 = grade_service.compute_class_rankings(cls1, t1)

print("Calcul des moyennes T1 — 5ème B...")
rankings_2 = grade_service.compute_class_rankings(cls2, t1)

print("Enrichissement des bulletins avec commentaires...")
comments_by_rank = {
    1: ("Excellent travail, félicitations ! Continuez ainsi.",
        "Admis(e) avec les félicitations du conseil de classe."),
    2: ("Très bon trimestre, résultats encourageants.",
        "Passage en classe supérieure accordé. Bravo !"),
    3: ("Bons résultats, effort notable dans toutes les matières.",
        "Passage accordé. Maintenir ces efforts."),
    4: ("Résultats corrects. Des progrès sont encore possibles.",
        "Passage accordé sous réserve."),
    5: ("Trimestre passable. Des lacunes persistent.",
        "Avertissement de travail. Redoubler d'efforts."),
    6: ("Résultats insuffisants. Un soutien est nécessaire.",
        "Mise en garde. Voir les parents."),
}
for rc in ReportCard.objects.filter(trimester=t1):
    rank = rc.rank or 99
    ct, pc = comments_by_rank.get(min(rank, 6), ("Résultats corrects.", "Passage accordé."))
    rc.class_teacher_comment = ct
    rc.principal_comment     = pc
    rc.conduct_grade = 'A+' if rank == 1 else ('A' if rank <= 3 else 'B')
    rc.status = 'published'
    rc.save()

print("Infos médicales de démonstration...")
for idx, student in enumerate(students_cls1[:3]):
    data = [
        dict(blood_type='A+', allergies='Pénicilline', emergency_contact_name='Kodjo Agbessi', emergency_contact_phone='+22961234567'),
        dict(blood_type='O+', allergies='', emergency_contact_name='Ama Mensah', emergency_contact_phone='+22967890123'),
        dict(blood_type='B+', allergies='Arachides, latex', medical_conditions='Asthme léger',
             emergency_contact_name='Yaw Dossou', emergency_contact_phone='+22969876543',
             doctor_name='Souza', doctor_phone='+22921234567'),
    ]
    MedicalInfo.objects.update_or_create(student=student, defaults=data[idx])

print("\n✅ Données supplémentaires créées !")
print(f"   Trimestres   : {Trimester.objects.count()}")
print(f"   Devoirs      : {Assignment.objects.count()}")
print(f"   Notes        : {Grade.objects.count()}")
print(f"   Présences    : {Attendance.objects.count()}")
print(f"   Notes matière: {SubjectGrade.objects.count()}")
print(f"   Bulletins    : {ReportCard.objects.count()}")
for rc in ReportCard.objects.filter(trimester=t1).order_by('rank'):
    print(f"   [{rc.rank:>2}] {rc.student.get_full_name():<25} → {rc.general_average}/20")
