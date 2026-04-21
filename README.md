# 🎓 EduPlatform — Plateforme de Gestion Scolaire

Une plateforme Django moderne, responsive et complète pour la gestion d'établissements scolaires.

---

## 🚀 Démarrage rapide

### Prérequis
- Python 3.10+
- pip

### Installation & lancement

```bash
# 1. Installer les dépendances
pip install django pillow

# 2. Lancer la plateforme (migrations + données démo incluses)
chmod +x start.sh
./start.sh

# Ou manuellement :
python manage.py migrate
python seed_data.py
python manage.py runserver
```

Ouvrez http://127.0.0.1:8000 dans votre navigateur.

---

## 👥 Comptes de démonstration

| Rôle         | Email                  | Mot de passe |
|------------- |------------------------|--------------|
| 👑 Admin      | admin@school.com       | demo1234     |
| 🎓 Enseignant | prof@school.com        | demo1234     |
| 📚 Élève      | eleve@school.com       | demo1234     |
| 👨‍👩‍👧 Parent    | parent@school.com      | demo1234     |

---

## ✨ Fonctionnalités

### 1. Gestion des utilisateurs
- 4 rôles : Administrateur, Enseignant, Élève, Parent
- Création/modification/suppression de comptes
- Authentification sécurisée (email + mot de passe)
- Gestion des avatars et profils détaillés
- Interface filtrée selon le rôle connecté

### 2. Gestion académique
- **Classes** : création avec niveau, capacité, année scolaire
- **Matières** : code, coefficient, couleur
- **Niveaux** : 6ème → Terminale
- **Affectation enseignants/classes** (ManyToMany)
- **Emploi du temps** : créneaux par jour, par classe, par enseignant

### 3. Devoirs & Examens
- Types : Devoir maison, Examen, Interrogation, Projet
- Échéances, note maximale, description
- Vues filtrées par rôle (enseignant voit ses devoirs, élève voit les siens)

### 4. Notes
- Saisie des notes par devoir/élève
- Barre de progression visuelle avec code couleur (vert/jaune/rouge)
- Calcul de la moyenne générale
- Commentaires personnalisés

### 5. Présences
- Statuts : Présent, Absent, En retard, Excusé
- Historique par élève
- Vue synthèse absences/présences

### 6. Inscriptions
- Inscription des élèves aux classes
- Suivi du taux de remplissage

### 7. Annonces & Communications
- Ciblage par rôle (tous, enseignants, élèves, parents)
- Annonces épinglées
- Fil d'actualité sur le tableau de bord

---

## 🏗️ Architecture

```
school_platform/
├── accounts/           # App utilisateurs
│   ├── models.py       # User, TeacherProfile, StudentProfile
│   ├── views.py        # Login, CRUD utilisateurs, profil
│   ├── forms.py        # Formulaires
│   └── urls.py
├── academic/           # App académique
│   ├── models.py       # Level, Subject, Classroom, Schedule, Assignment, Grade, Attendance, Announcement
│   ├── views.py        # Toutes les vues académiques
│   ├── forms.py
│   ├── urls.py
│   └── templatetags/   # Filtre dict_extras
├── templates/
│   ├── base.html       # Layout principal (sidebar + topbar)
│   ├── dashboard.html  # Tableau de bord dynamique par rôle
│   ├── accounts/       # login, user_list, user_form, profile
│   └── academic/       # Toutes les pages académiques
├── static/
│   └── css/main.css    # Design system complet (dark theme)
├── seed_data.py        # Données de démonstration
└── start.sh            # Script de démarrage
```

---

## 🎨 Design System

- **Thème** : Dark mode élégant (#0a0f1e)
- **Typographie** : Outfit + DM Serif Display (Google Fonts)
- **Couleurs** : Bleu accent (#4f9cf9), Violet (#7b5ea7), Vert (#38d4a4), Orange (#f97316)
- **Composants** : Cards, badges, tables, formulaires, avatars, stat-cards
- **Responsive** : Sidebar collapsible sur mobile, grilles adaptatives

---

## 🔧 Pour aller plus loin

### Production
```bash
# Variables d'environnement recommandées
export SECRET_KEY="votre-clé-secrète-longue"
export DEBUG=False
export DATABASE_URL="postgres://..."

# Base de données PostgreSQL
pip install psycopg2-binary

# Serveur WSGI
pip install gunicorn
gunicorn school_platform.wsgi:application
```

### Fonctionnalités à ajouter
- 📧 Envoi d'emails (notifications absences, nouvelles notes)
- 📊 Bulletins de notes PDF téléchargeables
- 📱 Notifications push
- 🔐 Authentification OTP (code par SMS)
- 📈 Statistiques avancées (courbes de progression)
- 💬 Messagerie interne parent/enseignant
- 📅 Calendrier scolaire interactif

---

## 📦 Dépendances

| Package | Version | Usage |
|---------|---------|-------|
| Django  | ≥ 4.2   | Framework principal |
| Pillow  | ≥ 10.0  | Gestion des images (avatars) |

---

*EduPlatform — Conçu pour les établissements scolaires francophones d'Afrique et d'Europe.*
# school_platform2
