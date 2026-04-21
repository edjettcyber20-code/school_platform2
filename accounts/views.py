from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from datetime import date

from .models import User, TeacherProfile, StudentProfile, MedicalInfo, Insurance
from .forms import (LoginForm, UserCreationForm, UserEditForm,
                    MedicalInfoForm, InsuranceForm)
from academic.models import Classroom, Assignment, Grade, Attendance, Announcement, Schedule


# ══════════════════════════════════════════════════════════════════════════════
# AUTH
# ══════════════════════════════════════════════════════════════════════════════
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect('dashboard')
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Déconnexion sécurisée — GET = confirmation, POST = exécution."""
    if request.method == 'POST':
        logout(request)
        messages.success(request, "Vous avez été déconnecté avec succès.")
        return redirect('login')
    # GET → page de confirmation
    return render(request, 'accounts/logout_confirm.html')


# ══════════════════════════════════════════════════════════════════════════════
# TABLEAU DE BORD
# ══════════════════════════════════════════════════════════════════════════════
@login_required
def dashboard(request):
    user = request.user
    ctx = {'user': user}

    if user.role == 'admin':
        ctx.update({
            'total_students':  User.objects.filter(role='student').count(),
            'total_teachers':  User.objects.filter(role='teacher').count(),
            'total_classes':   Classroom.objects.count(),
            'total_parents':   User.objects.filter(role='parent').count(),
            'recent_announcements': Announcement.objects.all()[:5],
            'recent_users':    User.objects.order_by('-date_joined')[:6],
        })
    elif user.role == 'teacher':
        my_classes = user.classrooms.all()
        ctx.update({
            'my_classes':     my_classes,
            'my_assignments': Assignment.objects.filter(teacher=user).order_by('-created_at')[:5],
            'announcements':  Announcement.objects.filter(target_role__in=['all', 'teacher'])[:5],
            'total_students': sum(c.student_count for c in my_classes),
        })
    elif user.role == 'student':
        ctx.update({
            'enrollments':          user.enrollments.filter(is_active=True),
            'my_grades':            Grade.objects.filter(student=user).order_by('-graded_at')[:5],
            'upcoming_assignments': Assignment.objects.filter(
                classroom__enrollments__student=user,
                classroom__enrollments__is_active=True
            ).order_by('due_date')[:5],
            'announcements': Announcement.objects.filter(target_role__in=['all', 'student'])[:5],
        })
    elif user.role == 'parent':
        ctx.update({
            'children':      user.children.all(),
            'announcements': Announcement.objects.filter(target_role__in=['all', 'parent'])[:5],
        })

    return render(request, 'dashboard.html', ctx)


# ══════════════════════════════════════════════════════════════════════════════
# UTILISATEURS
# ══════════════════════════════════════════════════════════════════════════════
@login_required
def user_list(request):
    if request.user.role != 'admin':
        return redirect('dashboard')
    role   = request.GET.get('role', '')
    search = request.GET.get('q', '')
    users  = User.objects.all()
    if role:
        users = users.filter(role=role)
    if search:
        users = users.filter(
            Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(email__icontains=search)
        )
    return render(request, 'accounts/user_list.html', {'users': users, 'role': role, 'search': search})


@login_required
def user_create(request):
    if request.user.role != 'admin':
        return redirect('dashboard')
    form = UserCreationForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        messages.success(request, f"Utilisateur {user.get_full_name()} créé avec succès.")
        return redirect('user_list')
    return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Créer un utilisateur'})


@login_required
def user_edit(request, pk):
    if request.user.role != 'admin':
        return redirect('dashboard')
    user = get_object_or_404(User, pk=pk)
    form = UserEditForm(request.POST or None, request.FILES or None, instance=user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Utilisateur modifié avec succès.")
        return redirect('user_list')
    return render(request, 'accounts/user_form.html', {
        'form': form, 'title': "Modifier l'utilisateur", 'edit_user': user
    })


@login_required
def user_delete(request, pk):
    if request.user.role != 'admin':
        return redirect('dashboard')
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, "Utilisateur supprimé.")
        return redirect('user_list')
    return render(request, 'accounts/user_confirm_delete.html', {'delete_user': user})


@login_required
def profile(request):
    form = UserEditForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Profil mis à jour.")
        return redirect('profile')
    return render(request, 'accounts/profile.html', {'form': form})


# ══════════════════════════════════════════════════════════════════════════════
# INFOS MÉDICALES  (tous rôles : élèves, enseignants, admins)
# ══════════════════════════════════════════════════════════════════════════════
@login_required
def medical_list(request):
    """Liste de tous les profils médicaux (admin/enseignant) ou profil perso (autres rôles)."""
    if request.user.role not in ('admin', 'teacher'):
        # Redirige vers sa propre fiche
        return redirect('medical_my')

    search = request.GET.get('q', '')
    role_filter = request.GET.get('role', '')

    users = User.objects.exclude(role='parent').select_related('medical_info')
    if search:
        users = users.filter(
            Q(first_name__icontains=search) | Q(last_name__icontains=search)
        )
    if role_filter:
        users = users.filter(role=role_filter)

    # Statistiques rapides
    total_with_info = MedicalInfo.objects.count()
    total_users = users.count()

    return render(request, 'accounts/medical_list.html', {
        'users': users,
        'total_with_info': total_with_info,
        'total_users': total_users,
        'search': search,
        'role_filter': role_filter,
    })


@login_required
def medical_my(request):
    """Fiche médicale de l'utilisateur connecté."""
    medical, _ = MedicalInfo.objects.get_or_create(user=request.user)
    return medical_edit_for(request, request.user.pk)


@login_required
def medical_edit_for(request, pk):
    """Édition de la fiche médicale d'un utilisateur donné."""
    target_user = get_object_or_404(User, pk=pk)

    # Contrôle d'accès
    if request.user.role not in ('admin', 'teacher') and request.user.pk != pk:
        messages.error(request, "Accès refusé.")
        return redirect('dashboard')

    medical, _ = MedicalInfo.objects.get_or_create(user=target_user)
    form = MedicalInfoForm(request.POST or None, instance=medical)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Informations médicales mises à jour.")
        # Retour intelligent selon le contexte
        if request.user.role == 'student':
            return redirect('medical_my')
        return redirect('medical_list')

    return render(request, 'accounts/medical_edit.html', {
        'target_user': target_user,
        'medical': medical,
        'form': form,
        'is_own': request.user.pk == pk,
    })


# ══════════════════════════════════════════════════════════════════════════════
# ASSURANCES
# ══════════════════════════════════════════════════════════════════════════════
@login_required
def insurance_list(request):
    """Liste des assurances — filtrée selon le rôle."""
    if request.user.role in ('admin', 'teacher'):
        search = request.GET.get('q', '')
        role_filter = request.GET.get('role', '')
        status_filter = request.GET.get('status', '')
        type_filter = request.GET.get('type', '')

        insurances = Insurance.objects.select_related('user').order_by('end_date')

        if search:
            insurances = insurances.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(company__icontains=search) |
                Q(policy_number__icontains=search)
            )
        if role_filter:
            insurances = insurances.filter(user__role=role_filter)
        if status_filter:
            insurances = insurances.filter(status=status_filter)
        if type_filter:
            insurances = insurances.filter(insurance_type=type_filter)

        # Stats
        today = date.today()
        expiring_soon = insurances.filter(
            end_date__gte=today,
            end_date__lte=today.replace(day=min(today.day + 30, 28))
        ).count()

        return render(request, 'accounts/insurance_list.html', {
            'insurances': insurances,
            'expiring_soon': expiring_soon,
            'search': search,
            'role_filter': role_filter,
            'status_filter': status_filter,
            'type_filter': type_filter,
            'type_choices': Insurance.TYPE_CHOICES,
            'status_choices': Insurance.STATUS_CHOICES,
        })
    else:
        # Élève/parent voit uniquement ses propres assurances
        insurances = Insurance.objects.filter(user=request.user)
        return render(request, 'accounts/insurance_list.html', {
            'insurances': insurances,
            'own_view': True,
        })


@login_required
def insurance_create(request):
    """Créer une assurance."""
    if request.user.role not in ('admin',):
        messages.error(request, "Seuls les administrateurs peuvent créer des assurances.")
        return redirect('insurance_list')

    # Pré-sélection d'un utilisateur si fourni en GET
    initial = {}
    user_pk = request.GET.get('user')
    if user_pk:
        initial['user'] = user_pk

    form = InsuranceForm(request.POST or None, request.FILES or None, initial=initial)
    if request.method == 'POST' and form.is_valid():
        ins = form.save()
        messages.success(request, f"Assurance créée pour {ins.user.get_full_name()}.")
        return redirect('insurance_list')
    return render(request, 'accounts/insurance_form.html', {
        'form': form, 'title': "Nouvelle assurance", 'action': 'create'
    })


@login_required
def insurance_edit(request, pk):
    """Modifier une assurance."""
    insurance = get_object_or_404(Insurance, pk=pk)
    if request.user.role != 'admin':
        messages.error(request, "Accès refusé.")
        return redirect('insurance_list')

    form = InsuranceForm(request.POST or None, request.FILES or None, instance=insurance)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Assurance mise à jour.")
        return redirect('insurance_list')
    return render(request, 'accounts/insurance_form.html', {
        'form': form, 'title': f"Modifier — {insurance}",
        'insurance': insurance, 'action': 'edit'
    })


@login_required
def insurance_delete(request, pk):
    """Supprimer une assurance."""
    insurance = get_object_or_404(Insurance, pk=pk)
    if request.user.role != 'admin':
        return redirect('insurance_list')
    if request.method == 'POST':
        insurance.delete()
        messages.success(request, "Assurance supprimée.")
        return redirect('insurance_list')
    return render(request, 'accounts/insurance_confirm_delete.html', {'insurance': insurance})


@login_required
def insurance_user(request, pk):
    """Toutes les assurances d'un utilisateur spécifique."""
    target_user = get_object_or_404(User, pk=pk)
    if request.user.role not in ('admin',) and request.user.pk != pk:
        return redirect('dashboard')
    insurances = Insurance.objects.filter(user=target_user)
    return render(request, 'accounts/insurance_user.html', {
        'target_user': target_user,
        'insurances': insurances,
    })
