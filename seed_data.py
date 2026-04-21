import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import TeacherProfile, StudentProfile
from academic.models import Level, Subject, Classroom, Enrollment, Schedule, Assignment, Grade, Attendance, Announcement
from datetime import date, datetime, timedelta
from django.utils import timezone

User = get_user_model()

# ✅ Nettoyage des données existantes pour éviter les doublons
print("🧹 Nettoyage des données existantes...")
Announcement.objects.all().delete()
Attendance.objects.all().delete()
Grade.objects.all().delete()
Assignment.objects.all().delete()
Schedule.objects.all().delete()
Enrollment.objects.all().delete()
Classroom.objects.all().delete()
Subject.objects.all().delete()
Level.objects.all().delete()
TeacherProfile.objects.all().delete()
StudentProfile.objects.all().delete()
User.objects.all().delete()

print("Création des utilisateurs...")

# Admin
admin = User.objects.create_superuser(
    username='admin', email='admin@school.com', password='demo1234',
    first_name='Marie', last_name='Dupont', role='admin'
)

# Teachers
t1 = User.objects.create_user(username='prof1', email='prof@school.com', password='demo1234',
    first_name='Jean', last_name='Martin', role='teacher', phone='+22961000001')
t2 = User.objects.create_user(username='prof2', email='prof2@school.com', password='demo1234',
    first_name='Ama', last_name='Koffi', role='teacher', phone='+22961000002')
t3 = User.objects.create_user(username='prof3', email='prof3@school.com', password='demo1234',
    first_name='Paul', last_name='Hounkpevi', role='teacher', phone='+22961000003')

TeacherProfile.objects.create(user=t1, employee_id='ENS001', specialization='Mathématiques', hire_date=date(2020,9,1))
TeacherProfile.objects.create(user=t2, employee_id='ENS002', specialization='Français', hire_date=date(2019,9,1))
TeacherProfile.objects.create(user=t3, employee_id='ENS003', specialization='Sciences', hire_date=date(2021,9,1))

# Students
students = []
noms = [('Kofi','Agbessi'),('Adjoa','Mensah'),('Yao','Dossou'),('Akosua','Tossou'),('Kwame','Afenyo'),
        ('Abena','Soglo'),('Kojo','Bello'),('Afi','Ahounou'),('Nana','Houeto'),('Sena','Kpade')]
for i,(fn,ln) in enumerate(noms):
    u = User.objects.create_user(username=f'eleve{i+1}', email=f'eleve{i+1}@school.com' if i>0 else 'eleve@school.com',
        password='demo1234', first_name=fn, last_name=ln, role='student', phone=f'+2296200000{i+1}')
    sp = StudentProfile.objects.create(user=u, student_id=f'STU{2024001+i}', enrollment_date=date(2024,9,1))
    students.append(u)

# Parents
p1 = User.objects.create_user(username='parent1', email='parent@school.com', password='demo1234',
    first_name='Kossi', last_name='Agbessi', role='parent', phone='+22993000001')
p2 = User.objects.create_user(username='parent2', email='parent2@school.com', password='demo1234',
    first_name='Felicite', last_name='Mensah', role='parent', phone='+22993000002')
students[0].student_profile.parents.add(p1)
students[1].student_profile.parents.add(p2)

print("Niveaux et matières...")
lv1 = Level.objects.create(name='6ème', order=1)
lv2 = Level.objects.create(name='5ème', order=2)
lv3 = Level.objects.create(name='Terminale', order=6)

maths = Subject.objects.create(name='Mathématiques', code='MATH', coefficient=4, color='#4f9cf9')
french = Subject.objects.create(name='Français', code='FRAN', coefficient=4, color='#f97316')
svt = Subject.objects.create(name='SVT', code='SVT', coefficient=3, color='#38d4a4')
histoire = Subject.objects.create(name='Histoire-Géo', code='HG', coefficient=3, color='#a78bfa')
physique = Subject.objects.create(name='Physique-Chimie', code='PHY', coefficient=3, color='#fb923c')
anglais = Subject.objects.create(name='Anglais', code='ANG', coefficient=2, color='#60a5fa')

print("Classes...")
cls1 = Classroom.objects.create(name='6ème A', level=lv1, capacity=35, school_year='2024-2025')
cls1.teachers.add(t1, t2, t3)
cls1.subjects.add(maths, french, svt, histoire, anglais)

cls2 = Classroom.objects.create(name='5ème B', level=lv2, capacity=32, school_year='2024-2025')
cls2.teachers.add(t1, t3)
cls2.subjects.add(maths, physique, svt, anglais)

cls3 = Classroom.objects.create(name='Terminale C', level=lv3, capacity=30, school_year='2024-2025')
cls3.teachers.add(t1, t2, t3)
cls3.subjects.add(maths, physique, svt, french, anglais)

# Enroll students
for i, st in enumerate(students[:6]):
    Enrollment.objects.create(student=st, classroom=cls1)
for st in students[6:]:
    Enrollment.objects.create(student=st, classroom=cls2)

print("Emploi du temps...")
slots = [
    (cls1, maths, t1, 'monday', '08:00', '09:00', 'Salle 101'),
    (cls1, french, t2, 'monday', '09:00', '10:00', 'Salle 101'),
    (cls1, svt, t3, 'tuesday', '08:00', '09:00', 'Labo A'),
    (cls1, histoire, t2, 'tuesday', '09:00', '10:00', 'Salle 102'),
    (cls1, anglais, t2, 'wednesday', '08:00', '09:00', 'Salle 103'),
    (cls1, maths, t1, 'thursday', '10:00', '11:00', 'Salle 101'),
    (cls2, maths, t1, 'monday', '10:00', '11:00', 'Salle 201'),
    (cls2, physique, t3, 'tuesday', '10:00', '11:00', 'Labo B'),
    (cls2, svt, t3, 'wednesday', '09:00', '10:00', 'Labo A'),
    (cls3, maths, t1, 'friday', '08:00', '10:00', 'Grande Salle'),
    (cls3, physique, t3, 'friday', '10:00', '12:00', 'Labo C'),
]
for cls, sub, tch, day, st, et, room in slots:
    Schedule.objects.create(classroom=cls, subject=sub, teacher=tch, day=day,
        start_time=st, end_time=et, room=room)

print("Devoirs et notes...")
a1 = Assignment.objects.create(title='Devoir sur les fractions', description='Exercices chapitres 1 à 3',
    type='homework', subject=maths, classroom=cls1, teacher=t1,
    due_date=timezone.now()+timedelta(days=7), max_score=20)
a2 = Assignment.objects.create(title='Examen de mi-trimestre - Français', type='exam',
    subject=french, classroom=cls1, teacher=t2,
    due_date=timezone.now()+timedelta(days=14), max_score=20)
a3 = Assignment.objects.create(title='Interrogation SVT - La cellule', type='quiz',
    subject=svt, classroom=cls1, teacher=t3,
    due_date=timezone.now()-timedelta(days=5), max_score=10)

# Grades for a3
scores = [8, 9, 7, 10, 6, 9.5]
comments = ['Bien', 'Très bien', 'À revoir', 'Parfait!', 'Insuffisant', 'Bien']
for i, (st, sc, cm) in enumerate(zip(students[:6], scores, comments)):
    Grade.objects.create(student=st, assignment=a3, score=sc, comment=cm)

a4 = Assignment.objects.create(title='Contrôle de Maths', type='exam',
    subject=maths, classroom=cls2, teacher=t1,
    due_date=timezone.now()-timedelta(days=10), max_score=20)
for i, st in enumerate(students[6:]):
    Grade.objects.create(student=st, assignment=a4, score=[15, 12, 18, 11][i], comment='')

print("Présences...")
sched1 = Schedule.objects.first()
if sched1:
    for i, st in enumerate(students[:4]):
        Attendance.objects.create(student=st, schedule=sched1, date=date.today()-timedelta(days=i),
            status='present' if i != 2 else 'absent', note='' if i != 2 else 'Non justifiée')

print("Annonces...")
Announcement.objects.create(title='Rentrée scolaire 2024-2025', 
    content='Bienvenue à tous les élèves, enseignants et parents pour cette nouvelle année scolaire. Les cours débutent le lundi 2 septembre. Merci de consulter régulièrement la plateforme pour les informations importantes.',
    author=admin, target_role='all', is_pinned=True)
Announcement.objects.create(title='Réunion des enseignants', 
    content='Une réunion pédagogique est prévue le vendredi 15 novembre à 15h en salle des professeurs. Présence obligatoire pour tous les enseignants.',
    author=admin, target_role='teacher')
Announcement.objects.create(title='Calendrier des examens du 1er trimestre',
    content='Les examens du premier trimestre se dérouleront du 2 au 13 décembre 2024. Les emplois du temps détaillés seront communiqués deux semaines avant le début des épreuves.',
    author=admin, target_role='all')
Announcement.objects.create(title='Réunion parents-professeurs',
    content='La réunion parents-professeurs du 1er trimestre aura lieu le samedi 30 novembre de 9h à 12h. Votre présence est vivement souhaitée pour le suivi de vos enfants.',
    author=admin, target_role='parent')

print("\n✅ Données de démonstration créées avec succès!")
print("="*50)
print("Comptes disponibles:")
print("  Admin    : admin@school.com / demo1234")
print("  Enseignant: prof@school.com / demo1234")
print("  Élève    : eleve@school.com / demo1234")
print("  Parent   : parent@school.com / demo1234")