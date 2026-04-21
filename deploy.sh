#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
#  EduPlatform — Script de déploiement production
# ═══════════════════════════════════════════════════════════════════
set -e

echo ""
echo "  ╔══════════════════════════════════════════════════╗"
echo "  ║   🎓  EduPlatform — Déploiement Production       ║"
echo "  ╚══════════════════════════════════════════════════╝"
echo ""

cd "$(dirname "$0")"

# ── 1. Dépendances ──────────────────────────────────────────────────
echo "📦  Installation des dépendances..."
pip install -r requirements.txt --break-system-packages -q

# ── 2. Variables d'environnement ────────────────────────────────────
if [ -f .env ]; then
  echo "⚙️   Chargement du fichier .env..."
  export $(grep -v '^#' .env | xargs)
fi

# Vérifications critiques
if [ -z "$SECRET_KEY" ]; then
  echo "⚠️   AVERTISSEMENT : SECRET_KEY non défini. Utilisation de la valeur par défaut (INSÉCURISÉ EN PRODUCTION)."
fi
if [ "$DEBUG" = "True" ]; then
  echo "⚠️   AVERTISSEMENT : DEBUG=True en production. Pensez à définir DEBUG=False."
fi

# ── 3. Migrations ────────────────────────────────────────────────────
echo "🗄️   Migrations de la base de données..."
python manage.py migrate --noinput

# ── 4. Collecte des fichiers statiques ──────────────────────────────
echo "📁  Collecte des fichiers statiques..."
python manage.py collectstatic --noinput --clear

# ── 5. Création superuser si besoin ─────────────────────────────────
echo "👤  Vérification du superuser..."
python -c "
import os, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'school_platform.settings'
django.setup()
from accounts.models import User
if not User.objects.filter(role='admin').exists():
    User.objects.create_superuser(
        username=os.environ.get('ADMIN_USERNAME', 'admin'),
        email=os.environ.get('ADMIN_EMAIL', 'admin@school.com'),
        password=os.environ.get('ADMIN_PASSWORD', 'changez-ce-mot-de-passe'),
        first_name='Admin', last_name='Principal', role='admin'
    )
    print('  ✅ Superuser admin créé.')
else:
    print('  ✓  Superuser existant.')
"

# ── 6. Lancement serveur ─────────────────────────────────────────────
PORT="${PORT:-8000}"
WORKERS="${WEB_WORKERS:-2}"

echo ""
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🚀  Démarrage gunicorn sur 0.0.0.0:$PORT ($WORKERS workers)"
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

exec gunicorn school_platform.wsgi:application \
  --bind "0.0.0.0:$PORT" \
  --workers "$WORKERS" \
  --access-logfile - \
  --error-logfile - \
  --timeout 120
