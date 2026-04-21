#!/bin/bash
echo ""
echo "  ╔═══════════════════════════════════════════╗"
echo "  ║   🎓  EduPlatform — Gestion Scolaire      ║"
echo "  ╚═══════════════════════════════════════════╝"
echo ""

cd "$(dirname "$0")"
pip install -r requirements.txt --break-system-packages -q 2>/dev/null

python manage.py migrate --run-syncdb -v 0 2>/dev/null

python -c "
import os, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'school_platform.settings'
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.exists():
    print('  ⏳  Initialisation des données de démonstration...')
    exec(open('seed_data.py').read())
    exec(open('seed_extra.py').read())
    print('  ✅  Données prêtes !')
"

echo ""
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🌐  Accès  : http://127.0.0.1:8000"
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  👑  Admin      : admin@school.com / demo1234"
echo "  🎓  Enseignant : prof@school.com / demo1234"
echo "  📚  Élève      : eleve@school.com / demo1234"
echo "  👨‍👩‍👧  Parent     : parent@school.com / demo1234"
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
python manage.py runserver 0.0.0.0:8000
