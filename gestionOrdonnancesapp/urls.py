from django.urls import path , include
from gestionOrdonnancesapp.views import DossierMedicaleView, LoginViews, AllergieView, MedicamentInteractionView, AllergyCheckView
from . import views

urlpatterns = [
   path('login',LoginViews.as_view()),
  # path('allergie/',AllergieView.as_view()),
   #path('allergie/<int:id>/',AllergieView.as_view()),
   path('dossierMedicale/',DossierMedicaleView.as_view()),
   path('dossierMedicale/<int:id>/',DossierMedicaleView.as_view()),
   path('check_interaction/<int:medicament1_id>/<int:medicament2_id>/', MedicamentInteractionView.as_view(), name='check_interaction'),
   path('check_allergy/<int:user_id>/<int:medicament_id>/', AllergyCheckView.as_view(), name='check_allergy'),
    #allergie
    path('allergie/', AllergieView.as_view(), name='allergie-list'),  # Pour lister les allergies et en créer de nouvelles
    path('allergie/<int:id>/', AllergieView.as_view(), name='allergie-detail'),  # Pour récupérer, mettre à jour ou supprimer une allergie par ID
   #ordonance
    path('ordonnances/', views.OrdonnanceView.as_view(), name='ordonnance_list'),
    path('ordonnances/<int:id>/', views.OrdonnanceView.as_view(), name='ordonnance_detail'),

    # EFFET
    path('effets/', views.EffetView.as_view(), name='effet_list'),
    path('effets/<int:id>/', views.EffetView.as_view(), name='effet_detail'),

    # MEDICAMENT
    path('medicaments/', views.MedicamentView.as_view(), name='medicament_list'),
    path('medicaments/<int:id>/', views.MedicamentView.as_view(), name='medicament_detail'),

    # MEDICAMENTORDONNANCE
    path('medicament_ordonnances/', views.MedicamentOrdonnanceView.as_view(), name='medicament_ordonnance_list'),
    path('medicament_ordonnances/<int:id>/', views.MedicamentOrdonnanceView.as_view(), name='medicament_ordonnance_detail'),
]