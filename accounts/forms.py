from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User, TeacherProfile, StudentProfile, MedicalInfo, Insurance


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': "Email ou nom d'utilisateur", 'class': 'form-input'
        }),
        label='Identifiant'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Mot de passe', 'class': 'form-input'})
    )


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input'}), label='Mot de passe')
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input'}), label='Confirmer le mot de passe')

    employee_id    = forms.CharField(required=False, label='N° employé',        widget=forms.TextInput(attrs={'class': 'form-input'}))
    specialization = forms.CharField(required=False, label='Spécialisation',    widget=forms.TextInput(attrs={'class': 'form-input'}))
    hire_date      = forms.DateField(required=False, label="Date d'embauche",   widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}))
    student_id     = forms.CharField(required=False, label='N° matricule',      widget=forms.TextInput(attrs={'class': 'form-input'}))
    enrollment_date= forms.DateField(required=False, label="Date d'inscription",widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'role',
                  'phone', 'date_of_birth', 'address']
        widgets = {
            'first_name':    forms.TextInput(attrs={'class': 'form-input'}),
            'last_name':     forms.TextInput(attrs={'class': 'form-input'}),
            'email':         forms.EmailInput(attrs={'class': 'form-input'}),
            'username':      forms.TextInput(attrs={'class': 'form-input'}),
            'role':          forms.Select(attrs={'class': 'form-select', 'id': 'id_role'}),
            'phone':         forms.TextInput(attrs={'class': 'form-input'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'address':       forms.Textarea(attrs={'class': 'form-input', 'rows': 2}),
        }

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
            self._create_profile(user)
        return user

    def _create_profile(self, user):
        from datetime import date
        if user.role == 'teacher':
            TeacherProfile.objects.get_or_create(user=user, defaults={
                'employee_id':    self.cleaned_data.get('employee_id') or f'EMP-{user.pk:04d}',
                'specialization': self.cleaned_data.get('specialization') or 'Général',
                'hire_date':      self.cleaned_data.get('hire_date') or date.today(),
            })
        elif user.role == 'student':
            StudentProfile.objects.get_or_create(user=user, defaults={
                'student_id':      self.cleaned_data.get('student_id') or f'EL-{user.pk:04d}',
                'enrollment_date': self.cleaned_data.get('enrollment_date') or date.today(),
            })


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'role', 'phone', 'date_of_birth', 'address', 'avatar']
        widgets = {
            'first_name':    forms.TextInput(attrs={'class': 'form-input'}),
            'last_name':     forms.TextInput(attrs={'class': 'form-input'}),
            'email':         forms.EmailInput(attrs={'class': 'form-input'}),
            'role':          forms.Select(attrs={'class': 'form-select'}),
            'phone':         forms.TextInput(attrs={'class': 'form-input'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'address':       forms.Textarea(attrs={'class': 'form-input', 'rows': 2}),
        }


class MedicalInfoForm(forms.ModelForm):
    class Meta:
        model = MedicalInfo
        exclude = ['user', 'updated_at']
        widgets = {
            'blood_type':                forms.Select(attrs={'class': 'form-select'}),
            'allergies':                 forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2}),
            'medical_conditions':        forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2}),
            'chronic_diseases':          forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2}),
            'current_medications':       forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2}),
            'vaccination_status':        forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2}),
            'emergency_contact_name':    forms.TextInput(attrs={'class': 'form-input'}),
            'emergency_contact_phone':   forms.TextInput(attrs={'class': 'form-input'}),
            'emergency_contact_relation':forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'ex: Père, Mère, Conjoint…'}),
            'doctor_name':               forms.TextInput(attrs={'class': 'form-input'}),
            'doctor_phone':              forms.TextInput(attrs={'class': 'form-input'}),
            'insurance_number':          forms.TextInput(attrs={'class': 'form-input'}),
            'last_checkup':              forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'notes':                     forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
        }


class InsuranceForm(forms.ModelForm):
    class Meta:
        model = Insurance
        fields = ['user', 'insurance_type', 'company', 'policy_number', 'beneficiary',
                  'start_date', 'end_date', 'coverage_amount', 'premium_amount',
                  'status', 'document', 'notes']
        widgets = {
            'user':             forms.Select(attrs={'class': 'form-select'}),
            'insurance_type':   forms.Select(attrs={'class': 'form-select'}),
            'status':           forms.Select(attrs={'class': 'form-select'}),
            'company':          forms.TextInput(attrs={'class': 'form-input'}),
            'policy_number':    forms.TextInput(attrs={'class': 'form-input'}),
            'beneficiary':      forms.TextInput(attrs={'class': 'form-input'}),
            'start_date':       forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'end_date':         forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'coverage_amount':  forms.NumberInput(attrs={'class': 'form-input'}),
            'premium_amount':   forms.NumberInput(attrs={'class': 'form-input'}),
            'notes':            forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Exclure les parents du choix utilisateur pour assurance
        self.fields['user'].queryset = User.objects.exclude(role='parent').order_by('role', 'last_name', 'first_name')
        self.fields['user'].label_from_instance = lambda u: f"{u.get_full_name()} ({u.get_role_display()})"
