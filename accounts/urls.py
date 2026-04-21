from django.urls import path
from . import views

urlpatterns = [
    # ── Auth ──────────────────────────────────────────────────────────────
    path('login/',                        views.login_view,        name='login'),
    path('logout/',                       views.logout_view,       name='logout'),
    path('dashboard/',                    views.dashboard,         name='dashboard'),

    # ── Profil ────────────────────────────────────────────────────────────
    path('profile/',                      views.profile,           name='profile'),

    # ── Utilisateurs ──────────────────────────────────────────────────────
    path('users/',                        views.user_list,         name='user_list'),
    path('users/create/',                 views.user_create,       name='user_create'),
    path('users/<int:pk>/edit/',          views.user_edit,         name='user_edit'),
    path('users/<int:pk>/delete/',        views.user_delete,       name='user_delete'),

    # ── Infos médicales ───────────────────────────────────────────────────
    path('sante/',                        views.medical_list,      name='medical_list'),
    path('sante/moi/',                    views.medical_my,        name='medical_my'),
    path('sante/<int:pk>/edit/',          views.medical_edit_for,  name='medical_edit_for'),

    # ── Assurances ────────────────────────────────────────────────────────
    path('assurances/',                   views.insurance_list,    name='insurance_list'),
    path('assurances/create/',            views.insurance_create,  name='insurance_create'),
    path('assurances/<int:pk>/edit/',     views.insurance_edit,    name='insurance_edit'),
    path('assurances/<int:pk>/delete/',   views.insurance_delete,  name='insurance_delete'),
    path('assurances/user/<int:pk>/',     views.insurance_user,    name='insurance_user'),
]
