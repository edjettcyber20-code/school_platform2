from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, TeacherProfile, StudentProfile, MedicalInfo, AcademicDocument, Insurance


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display  = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active']
    list_filter   = ['role', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Rôle & Contact', {'fields': ('role', 'phone', 'avatar', 'date_of_birth', 'address')}),
    )


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'employee_id', 'specialization', 'hire_date']


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'student_id', 'enrollment_date']


@admin.register(MedicalInfo)
class MedicalAdmin(admin.ModelAdmin):
    list_display = ['user', 'blood_type', 'emergency_contact_name', 'updated_at']
    search_fields = ['user__first_name', 'user__last_name']


@admin.register(AcademicDocument)
class DocAdmin(admin.ModelAdmin):
    list_display = ['student', 'title', 'doc_type', 'school_year', 'uploaded_at']


@admin.register(Insurance)
class InsuranceAdmin(admin.ModelAdmin):
    list_display = ['user', 'insurance_type', 'company', 'policy_number', 'start_date', 'end_date', 'status']
    list_filter  = ['insurance_type', 'status']
    search_fields = ['user__first_name', 'user__last_name', 'company', 'policy_number']
