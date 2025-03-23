from django.urls import path , include
from gestionOrdonnancesapp.views import DossierMedicaleView, LoginViews, AllergieView
from . import views

urlpatterns = [
   path('login',LoginViews.as_view()),
   path('allergie/',AllergieView.as_view()),
   path('allergie/<int:id>/',AllergieView.as_view()),
   path('dossierMedicale/',DossierMedicaleView.as_view()),
   path('dossierMedicale/<int:id>/',DossierMedicaleView.as_view()),
]