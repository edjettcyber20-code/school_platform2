from django.db import models
from accounts.models import User


class Level(models.Model):
    name = models.CharField(max_length=50)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    coefficient = models.IntegerField(default=1)
    color = models.CharField(max_length=7, default='#4F46E5')

    def __str__(self):
        return f"{self.name} ({self.code})"


class Classroom(models.Model):
    name = models.CharField(max_length=50)
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='classrooms')
    capacity = models.IntegerField(default=30)
    school_year = models.CharField(max_length=10, default='2024-2025')
    teachers = models.ManyToManyField(User, related_name='classrooms', blank=True, limit_choices_to={'role': 'teacher'})
    subjects = models.ManyToManyField(Subject, blank=True)

    def __str__(self):
        return f"{self.name} - {self.level.name}"

    @property
    def student_count(self):
        return self.enrollments.filter(is_active=True).count()


class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments', limit_choices_to={'role': 'student'})
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='enrollments')
    date_enrolled = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['student', 'classroom']

    def __str__(self):
        return f"{self.student.get_full_name()} -> {self.classroom.name}"


DAYS = [
    ('monday', 'Lundi'),
    ('tuesday', 'Mardi'),
    ('wednesday', 'Mercredi'),
    ('thursday', 'Jeudi'),
    ('friday', 'Vendredi'),
    ('saturday', 'Samedi'),
]


class Schedule(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='schedules')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'})
    day = models.CharField(max_length=10, choices=DAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.classroom} - {self.subject} ({self.day})"


class Assignment(models.Model):
    TYPE_CHOICES = [
        ('homework', 'Devoir maison'),
        ('exam', 'Examen'),
        ('quiz', 'Interrogation'),
        ('project', 'Projet'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='assignments')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'})
    due_date = models.DateTimeField()
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.classroom.name}"


class Grade(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grades', limit_choices_to={'role': 'student'})
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='grades')
    score = models.DecimalField(max_digits=5, decimal_places=2)
    comment = models.TextField(blank=True)
    graded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['student', 'assignment']

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.assignment.title}: {self.score}"


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'En retard'),
        ('excused', 'Excuse'),
    ]
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendances', limit_choices_to={'role': 'student'})
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')
    note = models.TextField(blank=True)

    class Meta:
        unique_together = ['student', 'schedule', 'date']

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.date} - {self.status}"


class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    target_role = models.CharField(max_length=20, choices=[('all', 'Tous'), ('teacher', 'Enseignants'), ('student', 'Eleves'), ('parent', 'Parents')], default='all')
    created_at = models.DateTimeField(auto_now_add=True)
    is_pinned = models.BooleanField(default=False)

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return self.title


class Trimester(models.Model):
    """Découpage de l'année scolaire en trimestres"""
    TRIMESTER_CHOICES = [('1','1er Trimestre'),('2','2ème Trimestre'),('3','3ème Trimestre')]
    school_year = models.CharField(max_length=10, default='2024-2025')
    number = models.CharField(max_length=1, choices=TRIMESTER_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)

    class Meta:
        unique_together = ['school_year', 'number']
        ordering = ['school_year', 'number']

    def __str__(self):
        return f"{self.get_number_display()} {self.school_year}"


class SubjectGrade(models.Model):
    """Note consolidée par matière, par élève, par trimestre (calculée automatiquement)"""
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subject_grades', limit_choices_to={'role':'student'})
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    trimester = models.ForeignKey(Trimester, on_delete=models.CASCADE)
    average = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    weighted_average = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    teacher_comment = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['student', 'subject', 'classroom', 'trimester']
        ordering = ['subject__name']

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.subject.name} T{self.trimester.number}: {self.average}"

    def compute_average(self):
        """Calcule la moyenne pondérée à partir des Assignment+Grade"""
        from django.db.models import Avg
        grades = Grade.objects.filter(
            student=self.student,
            assignment__subject=self.subject,
            assignment__classroom=self.classroom,
        )
        # Filter by trimester dates
        grades = grades.filter(
            assignment__due_date__date__gte=self.trimester.start_date,
            assignment__due_date__date__lte=self.trimester.end_date,
        )
        if not grades.exists():
            return None
        total_weighted = sum(float(g.score) / float(g.assignment.max_score) * 20 for g in grades)
        self.average = round(total_weighted / grades.count(), 2)
        # weighted by subject coefficient
        self.weighted_average = round(float(self.average) * self.subject.coefficient, 2)
        self.save(update_fields=['average', 'weighted_average', 'updated_at'])
        return self.average


class ReportCard(models.Model):
    """Bulletin de notes généré pour un élève sur un trimestre"""
    STATUS_CHOICES = [('draft','Brouillon'),('published','Publié'),('archived','Archivé')]
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='report_cards', limit_choices_to={'role':'student'})
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    trimester = models.ForeignKey(Trimester, on_delete=models.CASCADE)
    general_average = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    rank = models.IntegerField(null=True, blank=True)
    class_size = models.IntegerField(null=True, blank=True)
    class_average = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    highest_average = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    lowest_average = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    conduct_grade = models.CharField(max_length=2, default='B',
        choices=[('A+','Très bien'),('A','Bien'),('B','Assez bien'),('C','Passable'),('D','Insuffisant')])
    class_teacher_comment = models.TextField(blank=True)
    principal_comment = models.TextField(blank=True)
    absences_total = models.IntegerField(default=0)
    absences_justified = models.IntegerField(default=0)
    lates_total = models.IntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    pdf_file = models.FileField(upload_to='bulletins/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['student', 'classroom', 'trimester']
        ordering = ['-trimester__school_year', 'trimester__number']

    def __str__(self):
        return f"Bulletin {self.student.get_full_name()} - {self.trimester}"

    def compute_general_average(self):
        """Calcule la moyenne générale pondérée par coefficient"""
        sgs = SubjectGrade.objects.filter(student=self.student, classroom=self.classroom, trimester=self.trimester)
        if not sgs.exists():
            return None
        total_weighted = sum(float(sg.average or 0) * sg.subject.coefficient for sg in sgs if sg.average is not None)
        total_coeff = sum(sg.subject.coefficient for sg in sgs if sg.average is not None)
        if total_coeff == 0:
            return None
        self.general_average = round(total_weighted / total_coeff, 2)
        # Attendance
        atts = Attendance.objects.filter(
            student=self.student,
            date__gte=self.trimester.start_date,
            date__lte=self.trimester.end_date
        )
        self.absences_total = atts.filter(status='absent').count()
        self.absences_justified = atts.filter(status='excused').count()
        self.lates_total = atts.filter(status='late').count()
        self.save(update_fields=['general_average','absences_total','absences_justified','lates_total','updated_at'])
        return self.general_average
