from django.urls import path
from . import views, views_students, views_grades

urlpatterns = [
    # ── Niveaux ──────────────────────────────────────────────────────────
    path('niveaux/',                  views.level_list,    name='level_list'),
    path('niveaux/create/',           views.level_create,  name='level_create'),
    path('niveaux/<int:pk>/edit/',    views.level_edit,    name='level_edit'),
    path('niveaux/<int:pk>/delete/',  views.level_delete,  name='level_delete'),

    # ── Classes ───────────────────────────────────────────────────────────
    path('classes/',                  views.classroom_list,   name='classroom_list'),
    path('classes/create/',           views.classroom_create, name='classroom_create'),
    path('classes/<int:pk>/',         views.classroom_detail, name='classroom_detail'),
    path('classes/<int:pk>/edit/',    views.classroom_edit,   name='classroom_edit'),

    # ── Matières ──────────────────────────────────────────────────────────
    path('matieres/',                 views.subject_list,   name='subject_list'),
    path('matieres/create/',          views.subject_create, name='subject_create'),

    # ── Emploi du temps ───────────────────────────────────────────────────
    path('emploi-du-temps/',          views.schedule_view,   name='schedule_view'),
    path('emploi-du-temps/create/',   views.schedule_create, name='schedule_create'),

    # ── Devoirs & examens ─────────────────────────────────────────────────
    path('devoirs/',                  views.assignment_list,   name='assignment_list'),
    path('devoirs/create/',           views.assignment_create, name='assignment_create'),

    # ── Notes ─────────────────────────────────────────────────────────────
    path('notes/',                    views.grade_list,   name='grade_list'),
    path('notes/create/',             views.grade_create, name='grade_create'),

    # ── Présences ─────────────────────────────────────────────────────────
    path('presences/',                views.attendance_list,   name='attendance_list'),
    path('presences/create/',         views.attendance_create, name='attendance_create'),

    # ── Annonces ──────────────────────────────────────────────────────────
    path('annonces/',                 views.announcement_list,   name='announcement_list'),
    path('annonces/create/',          views.announcement_create, name='announcement_create'),

    # ── Inscriptions ──────────────────────────────────────────────────────
    path('inscriptions/create/',      views.enrollment_create, name='enrollment_create'),

    # ── Élèves ────────────────────────────────────────────────────────────
    path('eleves/',                              views_students.student_list,           name='student_list'),
    path('eleves/<int:pk>/',                     views_students.student_detail,          name='student_detail'),
    path('eleves/<int:pk>/presences/',           views_students.student_attendance_detail, name='student_attendance'),
    path('eleves/<int:pk>/medical/',             views_students.medical_edit,            name='medical_edit'),
    path('eleves/<int:pk>/documents/',           views_students.document_upload,         name='document_upload'),
    path('presences/saisie/',                    views_students.bulk_attendance,         name='bulk_attendance'),

    # ── Trimestres ────────────────────────────────────────────────────────
    path('trimestres/',               views_grades.trimester_list,   name='trimester_list'),
    path('trimestres/create/',        views_grades.trimester_create, name='trimester_create'),

    # ── Notes avancées ────────────────────────────────────────────────────
    path('devoirs/<int:assignment_id>/notes/',   views_grades.grade_entry,          name='grade_entry'),
    path('notes/matrice/',                       views_grades.grade_matrix,         name='grade_matrix'),
    path('notes/calculer/',                      views_grades.compute_averages,     name='compute_averages'),
    path('notes/matiere/<int:pk>/commentaire/',  views_grades.subject_grade_comment,name='sg_comment'),

    # ── Bulletins ─────────────────────────────────────────────────────────
    path('bulletins/',                    views_grades.report_card_list,    name='report_card_list'),
    path('bulletins/<int:pk>/',           views_grades.report_card_detail,  name='report_card_detail'),
    path('bulletins/<int:pk>/modifier/',  views_grades.report_card_edit,    name='report_card_edit'),
    path('bulletins/<int:pk>/pdf/',       views_grades.report_card_pdf,     name='report_card_pdf'),
    path('bulletins/<int:pk>/apercu/',    views_grades.report_card_preview, name='report_card_preview'),
    path('bulletins/generer/',            views_grades.generate_all_reports,name='generate_all_reports'),

    # ── Classement ────────────────────────────────────────────────────────
    path('classement/',               views_grades.class_ranking, name='class_ranking'),
]
