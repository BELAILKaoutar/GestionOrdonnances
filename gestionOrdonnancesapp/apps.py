from django.apps import AppConfig


class GestionordonnancesappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gestionOrdonnancesapp'

    def ready(self):
        import gestionOrdonnancesapp.signals