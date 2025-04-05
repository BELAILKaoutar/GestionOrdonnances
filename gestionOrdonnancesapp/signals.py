from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .models import DossierMedicale, Ordonnance, MedicamentOrdonnance, User

@receiver(post_save, sender=DossierMedicale)
def update_qr_on_dossier_save(sender, instance, **kwargs):
    instance.patient.generate_qr_code(force=True)
    instance.patient.save()

@receiver(post_save, sender=Ordonnance)
def update_qr_on_ordonnance_save(sender, instance, **kwargs):
    instance.dossierMedicale.patient.generate_qr_code(force=True)
    instance.dossierMedicale.patient.save()

@receiver(post_save, sender=MedicamentOrdonnance)
def update_qr_on_medicamentordonnance_save(sender, instance, **kwargs):
    instance.ordonnance.dossierMedicale.patient.generate_qr_code(force=True)
    instance.ordonnance.dossierMedicale.patient.save()

@receiver(m2m_changed, sender=DossierMedicale.allergies.through)
def update_qr_on_allergies_change(sender, instance, **kwargs):
    instance.patient.generate_qr_code(force=True)
    instance.patient.save()