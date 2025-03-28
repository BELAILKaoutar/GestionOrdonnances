from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.hashers import make_password
from django_mysql.models import ListCharField
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
import logging

logger = logging.getLogger(__name__)

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

    def generate_qr_code(self):
        """Génère un QR code contenant les infos du patient, son dossier médical et ses ordonnances."""
        if self.role.role == "P":
            data = {
                "CIN": self.cin,
                "Nom": self.firstName,
                "Prénom": self.lastName,
                "Âge": self.age,
                "Adresse": self.address,
            }

            # Ajouter les infos du dossier médical si elles existent
            if hasattr(self, 'dossier_medical'):
                dossier = self.dossier_medical
                data.update({
                    "Groupe Sanguin": dossier.bloodType,
                    "Tension": dossier.tension,
                    "Maladies Chroniques": dossier.maladieChronique,
                    "Antécédents Chirurgicaux": dossier.antecedentsChirurgicaux,
                    "Contact Urgence": dossier.contactUrgence,
                })

                # Ajouter les ordonnances
                ordonnances = dossier.ordonnances.all()
                data["Ordonnances"] = [{"Médicament": o.medicine_name, "Dosage": o.dosage} for o in ordonnances]

            # Générer le QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(str(data))
            qr.make(fit=True)

            img = qr.make_image(fill="black", back_color="white")

            # Sauvegarde dans l'image
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            self.qr_code.save(f"qr_{self.cin}.png", ContentFile(buffer.getvalue()), save=False)

    def save(self, *args, **kwargs):
        """Hacher le mot de passe et générer un QR code avant la sauvegarde."""
        if not self.password.startswith("pbkdf2_sha256$"):  # Vérifie si le mot de passe est déjà haché
            self.password = make_password(self.password)

        if self.role.role == "P":  # Vérifier si c'est un patient
            self.generate_qr_code()

        super().save(*args, **kwargs)




