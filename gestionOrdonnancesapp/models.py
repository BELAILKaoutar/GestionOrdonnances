from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.hashers import make_password
from django_mysql.models import ListCharField
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
import logging
from django.forms.models import model_to_dict
from django.core.files.base import ContentFile
logger = logging.getLogger(__name__)
from datetime import datetime
import json
import os
from django.core.files import File
class Role(models.Model):
    ROLE_CHOICES = [
        ("M", "Médecin"),
        ("P", "Patient"),
    ]
    id = models.AutoField(primary_key=True)
    role = models.CharField(max_length=1, choices=ROLE_CHOICES, unique=True)

    def __str__(self):
        return self.get_role_display()


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        
        # Generate QR code for new patients
        if extra_fields.get('role').role == "P":
            user.generate_qr_code()
        
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.contrib.auth.hashers import make_password
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    cin = models.CharField(max_length=10, unique=True)
    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=50)
    age = models.IntegerField()
    address = models.CharField(max_length=100)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, limit_choices_to={"role__in": ["P", "M"]})
    qr_code = models.ImageField(upload_to="qr_codes/", blank=True, null=True)

    groups = models.ManyToManyField("auth.Group", related_name="custom_user_groups", blank=True)
    user_permissions = models.ManyToManyField("auth.Permission", related_name="custom_user_permissions", blank=True)

    USERNAME_FIELD = 'email'

    objects = UserManager()


    def generate_qr_code(self, force=False):
        """Génère un QR code avec encodage correct des caractères spéciaux"""
        if self.role.role != "P":
            return
            
        if not force and self.qr_code:
            return
        
        # Delete old QR if exists
        if self.qr_code:
            try:
                os.remove(self.qr_code.path)
            except:
                pass
        
        # Base patient information
        data = {
            "CIN": self.cin,
            "Nom": self.lastName,
            "Prénom": self.firstName,
            "Âge": self.age,
            "Adresse": self.address,
            "Email": self.email,
        }

        try:
            dossier = self.dossier_medical
            dossier_data = {
                "Groupe sanguin": dossier.bloodType,
                "Tension": dossier.tension,
                "Maladies chroniques": dossier.maladieChronique,
                "Antécédents chirurgicaux": dossier.antecedentsChirurgicaux,
                "Contact urgence": dossier.contactUrgence,
            }

            # Add allergies
            allergies = dossier.allergies.all()
            dossier_data["Allergies"] = [
                {
                    "Nom": a.nom,
                    "Type": a.type,
                    "Gravité": a.gravite,
                    "Symptômes": a.symptomes,
                    "Traitement": a.traitement
                } for a in allergies
            ]

            # Add prescriptions
            ordonnances = dossier.ordonnances.all()
            prescriptions = []
            for ordonnance in ordonnances:
                ord_data = {
                    "Code ordonnance": ordonnance.code,
                    "Médicaments": []
                }
                
                medicaments = ordonnance.medicaments_prescrits.all()
                for med in medicaments:
                    med_data = {
                        "Nom": med.medicament.nom,
                        "Description": med.medicament.description,
                        "Posologie": med.posologie,
                        "Voie administration": med.medicament.voie_administration
                    }
                    ord_data["Médicaments"].append(med_data)
                
                prescriptions.append(ord_data)

            dossier_data["Ordonnances"] = prescriptions
            data["Dossier Médical"] = dossier_data

        except DossierMedicale.DoesNotExist:
            data["Dossier Médical"] = "Aucun dossier médical trouvé"
        except Exception as e:
            logger.error(f"Error generating QR code data: {str(e)}")
            data["Dossier Médical"] = "Erreur lors de la récupération du dossier"

        # Convert to JSON with proper encoding
        json_data = json.dumps(data, ensure_ascii=False, indent=2)
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(json_data)
        qr.make(fit=True)

        img = qr.make_image(fill="black", back_color="white")

        # Save image
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        filename = f"qr_{self.cin}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        
        # Properly save the file
        self.qr_code.save(
            filename,
            ContentFile(buffer.getvalue()),
            save=False
        )
    def save(self, *args, **kwargs):
        """Hacher le mot de passe et générer un QR code avant la sauvegarde."""
        if not self.password.startswith("pbkdf2_sha256$"):
            self.password = make_password(self.password)
        
        super().save(*args, **kwargs)  # Save first to ensure we have an ID
        
        if self.role.role == "P":
            self.generate_qr_code(force=True)  # Force regeneration after save


BloodTypes=[("A+","A+"),("A-","A-"),("B+","B+"),("B-","B-"),("O+","O+"),("O-","O-"),("AB+","AB+"),("AB-","AB-")]

class Allergie(models.Model):
    code=models.CharField(max_length=255, unique=True)
    nom=models.CharField(max_length=255) 
    type=models.CharField(max_length=255) #Alimentaire, médicamenteuse, environnementale...
    gravite=models.CharField(max_length=100,choices=[('Légère','Légère'),('modérée','modérée'),('sévère','sévère')]) 
    symptomes=models.TextField()
    traitement=models.TextField()
    def __str__(self):
        return f"{self.nom} ({self.type}) - Gravité: {self.gravite}" 

   
class Ordonnance(models.Model):
    code = models.CharField(max_length=255, unique=True)
    dossierMedicale = models.ForeignKey("gestionOrdonnancesapp.DossierMedicale", on_delete=models.CASCADE, related_name="ordonnances")

class DossierMedicale(models.Model):
    code=models.CharField(max_length=255, unique=True)
    patient = models.OneToOneField("User", on_delete=models.CASCADE, related_name="dossier_medical")
    bloodType=models.CharField(max_length=5, choices=BloodTypes,null=True, blank=True)
    tension=models.CharField(max_length=255)
    allergies=models.ManyToManyField(Allergie, blank=True, related_name="dossiers_medicaux")
    maladieChronique=models.TextField(blank=True, null=True)
    antecedentsChirurgicaux=models.TextField(blank=True, null=True)
    contactUrgence=models.CharField(max_length=255, blank=True, null=True)
    creation=models.DateTimeField(auto_now_add=True)
    miseAJour=models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Dossier Médical de {getattr(self.patient, 'firstName', 'Inconnu')} {getattr(self.patient, 'lastName', 'Inconnu')}"
    
class Effet(models.Model):
    code = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    gravite = models.CharField(max_length=100, choices=[('Légère', 'Légère'), ('Modérée', 'Modérée'), ('Sévère', 'Sévère')])
    medicaments = models.ManyToManyField("Medicament", related_name="effets_secondaires")

    def __str__(self):
        return f"{self.description} (Gravité : {self.gravite})"
 
class Medicament(models.Model):
    VOIES_ADMINISTRATION = [
        ("Orale", "Orale"),
        ("Injectable", "Injectable"),
        ("Topique", "Topique"),
        ("Inhalée", "Inhalée"),
        ("Sublinguale", "Sublinguale"),
        ("Rectale", "Rectale"),
    ]
    
    code = models.CharField(max_length=255, unique=True)
    nom = models.CharField(max_length=255)
    description = models.TextField(default="")  # Texte vide par défaut
    prix = models.FloatField(default=0.0)  # Prix du médicament
    disponibilite = models.BooleanField(default=True)  # Indique si le médicament est disponible ou non
    voie_administration = models.CharField(
        max_length=50,
        choices=VOIES_ADMINISTRATION,
        default="Orale"
    )  # Mode d'administration avec choix prédéfinis
    molecule_active = models.CharField(max_length=255, blank=True, null=True)  # Molécule active du médicament
    duree_traitement = models.IntegerField(help_text="Durée du traitement en jours",
    default=7)  # Durée du traitement

    effets = models.ManyToManyField(Effet, blank=True, related_name="medicaments_relations")  # Effets secondaires du médicament
    interactions = models.ManyToManyField(
        "self",
        blank=True,
        symmetrical=False,
        related_name="interactions_medicamenteuses"
    )  # Médicaments avec lesquels il peut interagir

    def __str__(self):
        return f"Medicament: {self.nom} ({self.molecule_active}) - {self.voie_administration}"

    
class MedicamentOrdonnance(models.Model):
    ordonnance = models.ForeignKey(Ordonnance, on_delete=models.CASCADE, related_name="medicaments_prescrits")
    medicament = models.ForeignKey(Medicament, on_delete=models.CASCADE, related_name="ordonnances_medicamenteuses")
    posologie = models.TextField()  # Ex: "2 comprimés par jour pendant 5 jours"

    def __str__(self):
        return f"{self.medicament.nom} (Ordonnance {self.ordonnance.code})"




