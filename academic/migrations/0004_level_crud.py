"""
Migration vide — aucun changement DB pour les niveaux.
Le modèle Level existait déjà depuis 0001_initial.
Ce fichier est un marqueur de version pour les nouvelles vues CRUD.
"""
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('academic', '0003_trimester_subjectgrade_reportcard'),
    ]
    operations = []
