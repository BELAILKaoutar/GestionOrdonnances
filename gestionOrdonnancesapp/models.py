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
BloodTypes=[("A+","A+"),("A-","A-"),("B+","B+"),("B-","B-"),("O+","O+"),("O-","O-"),("AB+","AB+"),("AB-","AB-")]

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

   
class Ordannance(models.Model):
    code=models.CharField(max_length=255, unique=True)
    dossierMedicale=models.ForeignKey("DossierMedicale",on_delete=models.CASCADE, related_name="ordonnances")

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
 


