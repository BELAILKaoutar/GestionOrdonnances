from django.urls import path , include
from gestionOrdonnancesapp.views import DossierMedicaleView, LoginViews, AllergieView, MedicamentInteractionView, AllergyCheckView
from . import views

urlpatterns = [
   path('login',LoginViews.as_view()),
   path('allergie/',AllergieView.as_view()),
   path('allergie/<int:id>/',AllergieView.as_view()),
   path('dossierMedicale/',DossierMedicaleView.as_view()),
   path('dossierMedicale/<int:id>/',DossierMedicaleView.as_view()),
   path('check_interaction/<int:medicament1_id>/<int:medicament2_id>/', MedicamentInteractionView.as_view(), name='check_interaction'),
   path('check_allergy/<int:user_id>/<int:medicament_id>/', AllergyCheckView.as_view(), name='check_allergy'),
]