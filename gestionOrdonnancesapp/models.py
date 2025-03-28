from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.hashers import make_password
from django_mysql.models import ListCharField

class Role(models.Model):
    ROLE_CHOICES = [
        ("M", "Medecin"),
        ("P", "Patient"),
    ]
    id = models.AutoField(primary_key=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    cin = models.CharField(max_length=10)
    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=50)
    age = models.IntegerField()
    address = models.CharField(max_length=100)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_user_groups",
        blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="custom_user_permissions",
        blank=True
    )

    USERNAME_FIELD = 'email'

    objects = UserManager()

    def save(self, *args, **kwargs):
        self.password = make_password(self.password)
        super().save(*args, **kwargs)

BloodTypes=[("A+","A+"),("A-","A-"),("B+","B+"),("B-","B-"),("O+","O+"),("O-","O-"),("AB+","AB+"),("AB-","AB-")]

class Allergie(models.Model):
    code=models.CharField(max_length=255, unique=True)
    nom=models.CharField(max_length=255) 
    type=models.CharField(max_length=255) #Alimentaire, médicamenteuse, environnementale...
    gravite=models.CharField(max_length=100,choices=[('Légère','Légère'),('modérée','modérée'),('sévère','sévère')]) 
    symptomes=models.TextField()
    traitement=models.TextField()
    #dossierMedicale=models.ManyToManyField("DossierMedicale", blank=True, related_name="allergies")
    def __str__(self):
        return f"{self.nom} ({self.type}) - Gravité: {self.gravite}" 

   
class Ordonnance(models.Model):
    code = models.CharField(max_length=255, unique=True)
    dossierMedicale = models.ForeignKey("DossierMedicale", on_delete=models.CASCADE, related_name="ordonnances")

class DossierMedicale(models.Model):
    code=models.CharField(max_length=255, unique=True)
    patient = models.OneToOneField("User", on_delete=models.CASCADE, related_name="dossier_medical")
    bloodType=models.CharField(max_length=5, choices=BloodTypes,null=True, blank=True)
    tension=models.CharField(max_length=255)
    allergies=models.ManyToManyField(Allergie, blank=True, related_name="dossiers_medicaux")
    maladieChronique=models.TextField(blank=True, null=True)
    #ordonnances = models.ForeignKey(Ordannance, related_name="dossier_medical")
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
    



