# Generated by Django 5.1.7 on 2025-04-02 22:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Allergie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=255, unique=True)),
                ('nom', models.CharField(max_length=255)),
                ('type', models.CharField(max_length=255)),
                ('gravite', models.CharField(choices=[('Légère', 'Légère'), ('modérée', 'modérée'), ('sévère', 'sévère')], max_length=100)),
                ('symptomes', models.TextField()),
                ('traitement', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Effet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=255, unique=True)),
                ('description', models.TextField()),
                ('gravite', models.CharField(choices=[('Légère', 'Légère'), ('Modérée', 'Modérée'), ('Sévère', 'Sévère')], max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('role', models.CharField(choices=[('M', 'Médecin'), ('P', 'Patient')], max_length=1, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='DossierMedicale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=255, unique=True)),
                ('bloodType', models.CharField(blank=True, choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-')], max_length=5, null=True)),
                ('tension', models.CharField(max_length=255)),
                ('maladieChronique', models.TextField(blank=True, null=True)),
                ('antecedentsChirurgicaux', models.TextField(blank=True, null=True)),
                ('contactUrgence', models.CharField(blank=True, max_length=255, null=True)),
                ('creation', models.DateTimeField(auto_now_add=True)),
                ('miseAJour', models.DateTimeField(auto_now=True)),
                ('allergies', models.ManyToManyField(blank=True, related_name='dossiers_medicaux', to='gestionOrdonnancesapp.allergie')),
            ],
        ),
        migrations.CreateModel(
            name='Medicament',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=255, unique=True)),
                ('nom', models.CharField(max_length=255)),
                ('description', models.TextField(default='')),
                ('prix', models.FloatField(default=0.0)),
                ('disponibilite', models.BooleanField(default=True)),
                ('voie_administration', models.CharField(choices=[('Orale', 'Orale'), ('Injectable', 'Injectable'), ('Topique', 'Topique'), ('Inhalée', 'Inhalée'), ('Sublinguale', 'Sublinguale'), ('Rectale', 'Rectale')], default='Orale', max_length=50)),
                ('molecule_active', models.CharField(blank=True, max_length=255, null=True)),
                ('duree_traitement', models.IntegerField(default=7, help_text='Durée du traitement en jours')),
                ('effets', models.ManyToManyField(blank=True, related_name='medicaments_relations', to='gestionOrdonnancesapp.effet')),
                ('interactions', models.ManyToManyField(blank=True, related_name='interactions_medicamenteuses', to='gestionOrdonnancesapp.medicament')),
            ],
        ),
        migrations.AddField(
            model_name='effet',
            name='medicaments',
            field=models.ManyToManyField(related_name='effets_secondaires', to='gestionOrdonnancesapp.medicament'),
        ),
        migrations.CreateModel(
            name='Ordonnance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=255, unique=True)),
                ('dossierMedicale', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ordonnances', to='gestionOrdonnancesapp.dossiermedicale')),
            ],
        ),
        migrations.CreateModel(
            name='MedicamentOrdonnance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('posologie', models.TextField()),
                ('medicament', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ordonnances_medicamenteuses', to='gestionOrdonnancesapp.medicament')),
                ('ordonnance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='medicaments_prescrits', to='gestionOrdonnancesapp.ordonnance')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('cin', models.CharField(max_length=10, unique=True)),
                ('firstName', models.CharField(max_length=50)),
                ('lastName', models.CharField(max_length=50)),
                ('age', models.IntegerField()),
                ('address', models.CharField(max_length=100)),
                ('qr_code', models.ImageField(blank=True, null=True, upload_to='qr_codes/')),
                ('groups', models.ManyToManyField(blank=True, related_name='custom_user_groups', to='auth.group')),
                ('role', models.ForeignKey(limit_choices_to={'role__in': ['P', 'M']}, on_delete=django.db.models.deletion.CASCADE, to='gestionOrdonnancesapp.role')),
                ('user_permissions', models.ManyToManyField(blank=True, related_name='custom_user_permissions', to='auth.permission')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='dossiermedicale',
            name='patient',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='dossier_medical', to='gestionOrdonnancesapp.user'),
        ),
    ]
