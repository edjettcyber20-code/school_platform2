from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('teacher', 'Enseignant'),
        ('student', 'Eleve'),
        ('parent', 'Parent'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    otp_code = models.CharField(max_length=6, blank=True)
    otp_expiry = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

    @property
    def is_admin_role(self):
        return self.role == 'admin'

    @property
    def is_teacher(self):
        return self.role == 'teacher'

    @property
    def is_student(self):
        return self.role == 'student'

    @property
    def is_parent_role(self):
        return self.role == 'parent'


class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    specialization = models.CharField(max_length=100)
    hire_date = models.DateField()

    def __str__(self):
        return f"Prof. {self.user.get_full_name()}"


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True)
    enrollment_date = models.DateField()
    parents = models.ManyToManyField(User, related_name='children', blank=True, limit_choices_to={'role': 'parent'})

    def __str__(self):
        return f"Eleve {self.user.get_full_name()} ({self.student_id})"


class MedicalInfo(models.Model):
    """Informations médicales — couvre élèves, enseignants et personnel administratif."""
    BLOOD_TYPES = [
        ('A+','A+'),('A-','A-'),('B+','B+'),('B-','B-'),
        ('AB+','AB+'),('AB-','AB-'),('O+','O+'),('O-','O-'),
        ('','Non renseigné'),
    ]
    # Champ renommé 'user' (couvre tous les rôles) — migration 0003
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='medical_info'
    )
    blood_type = models.CharField(max_length=4, choices=BLOOD_TYPES, blank=True)
    allergies = models.TextField(blank=True)
    medical_conditions = models.TextField(blank=True, verbose_name='Conditions médicales')
    chronic_diseases = models.TextField(blank=True, verbose_name='Maladies chroniques')
    current_medications = models.TextField(blank=True, verbose_name='Médicaments en cours')
    vaccination_status = models.TextField(blank=True, verbose_name='Vaccinations')
    # Contact d'urgence
    emergency_contact_name = models.CharField(max_length=100, blank=True, verbose_name='Contact urgence')
    emergency_contact_phone = models.CharField(max_length=20, blank=True, verbose_name='Tél. urgence')
    emergency_contact_relation = models.CharField(max_length=50, blank=True, verbose_name='Lien (père, mère…)')
    # Médecin
    doctor_name = models.CharField(max_length=100, blank=True, verbose_name='Médecin traitant')
    doctor_phone = models.CharField(max_length=20, blank=True)
    # Numéro assurance (quick-link — détail dans Insurance)
    insurance_number = models.CharField(max_length=50, blank=True, verbose_name='N° assurance santé')
    # Métadonnées
    last_checkup = models.DateField(null=True, blank=True, verbose_name='Dernier bilan médical')
    notes = models.TextField(blank=True, verbose_name='Observations libres')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Information médicale'
        verbose_name_plural = 'Informations médicales'

    def __str__(self):
        return f"Santé — {self.user.get_full_name()}"


class Insurance(models.Model):
    """Assurance pour élèves, enseignants et personnel administratif."""
    TYPE_CHOICES = [
        ('scolaire',    'Assurance scolaire'),
        ('sante',       'Assurance santé'),
        ('vie',         'Assurance vie'),
        ('accident',    'Assurance accident'),
        ('rc',          'Responsabilité civile'),
        ('professionnelle', 'Assurance professionnelle'),
        ('autre',       'Autre'),
    ]
    STATUS_CHOICES = [
        ('active',   'Active'),
        ('expired',  'Expirée'),
        ('pending',  'En attente'),
        ('cancelled','Résiliée'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='insurances'
    )
    insurance_type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Type d'assurance")
    company = models.CharField(max_length=100, verbose_name='Compagnie')
    policy_number = models.CharField(max_length=60, verbose_name='N° police / contrat')
    beneficiary = models.CharField(max_length=150, blank=True, verbose_name='Bénéficiaire(s)')
    start_date = models.DateField(verbose_name='Date de début')
    end_date = models.DateField(verbose_name="Date d'expiration")
    coverage_amount = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        verbose_name='Montant couvert (FCFA)'
    )
    premium_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name='Prime annuelle (FCFA)'
    )
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='active')
    document = models.FileField(upload_to='insurances/', blank=True, null=True, verbose_name='Document')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Assurance'
        verbose_name_plural = 'Assurances'

    def __str__(self):
        return f"{self.get_insurance_type_display()} — {self.user.get_full_name()} ({self.company})"

    @property
    def is_active(self):
        from datetime import date
        return self.status == 'active' and self.end_date >= date.today()

    @property
    def days_until_expiry(self):
        from datetime import date
        delta = self.end_date - date.today()
        return delta.days


class AcademicDocument(models.Model):
    DOC_TYPES = [
        ('certificate', 'Certificat de scolarité'),
        ('report', 'Bulletin de notes'),
        ('other', 'Autre document'),
    ]
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='documents',
        limit_choices_to={'role': 'student'}
    )
    title = models.CharField(max_length=200)
    doc_type = models.CharField(max_length=20, choices=DOC_TYPES)
    file = models.FileField(upload_to='documents/', blank=True, null=True)
    school_year = models.CharField(max_length=10, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.title} - {self.student.get_full_name()}"
