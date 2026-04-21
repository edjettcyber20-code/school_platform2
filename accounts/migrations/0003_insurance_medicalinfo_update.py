from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_academicdocument_medicalinfo'),
    ]

    operations = [
        # ── MedicalInfo : renommer 'student' → 'user' + nouveaux champs ──
        migrations.RenameField(
            model_name='medicalinfo',
            old_name='student',
            new_name='user',
        ),
        migrations.AlterField(
            model_name='medicalinfo',
            name='user',
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='medical_info',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='medicalinfo',
            name='chronic_diseases',
            field=models.TextField(blank=True, verbose_name='Maladies chroniques'),
        ),
        migrations.AddField(
            model_name='medicalinfo',
            name='current_medications',
            field=models.TextField(blank=True, verbose_name='Médicaments en cours'),
        ),
        migrations.AddField(
            model_name='medicalinfo',
            name='vaccination_status',
            field=models.TextField(blank=True, verbose_name='Vaccinations'),
        ),
        migrations.AddField(
            model_name='medicalinfo',
            name='emergency_contact_relation',
            field=models.CharField(blank=True, max_length=50, verbose_name='Lien (père, mère…)'),
        ),
        migrations.AddField(
            model_name='medicalinfo',
            name='last_checkup',
            field=models.DateField(blank=True, null=True, verbose_name='Dernier bilan médical'),
        ),
        migrations.AddField(
            model_name='medicalinfo',
            name='notes',
            field=models.TextField(blank=True, verbose_name='Observations libres'),
        ),
        migrations.AddField(
            model_name='medicalinfo',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),

        # ── Nouveau modèle Insurance ──────────────────────────────────────
        migrations.CreateModel(
            name='Insurance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('insurance_type', models.CharField(
                    choices=[
                        ('scolaire','Assurance scolaire'),('sante','Assurance santé'),
                        ('vie','Assurance vie'),('accident','Assurance accident'),
                        ('rc','Responsabilité civile'),('professionnelle','Assurance professionnelle'),
                        ('autre','Autre'),
                    ],
                    max_length=20, verbose_name="Type d'assurance"
                )),
                ('company', models.CharField(max_length=100, verbose_name='Compagnie')),
                ('policy_number', models.CharField(max_length=60, verbose_name='N° police / contrat')),
                ('beneficiary', models.CharField(blank=True, max_length=150, verbose_name='Bénéficiaire(s)')),
                ('start_date', models.DateField(verbose_name='Date de début')),
                ('end_date', models.DateField(verbose_name="Date d'expiration")),
                ('coverage_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='Montant couvert (FCFA)')),
                ('premium_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Prime annuelle (FCFA)')),
                ('status', models.CharField(
                    choices=[('active','Active'),('expired','Expirée'),('pending','En attente'),('cancelled','Résiliée')],
                    default='active', max_length=15
                )),
                ('document', models.FileField(blank=True, null=True, upload_to='insurances/', verbose_name='Document')),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='insurances',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={'ordering': ['-start_date'], 'verbose_name': 'Assurance', 'verbose_name_plural': 'Assurances'},
        ),
    ]
