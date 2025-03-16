from django.urls import path , include
from gestionOrdonnancesapp.views import LoginViews, AllergieView
from . import views

urlpatterns = [
   path('login',LoginViews.as_view()),
   path('allergie/',AllergieView.as_view()),
   path('allergie/<int:id>/',AllergieView.as_view()),
]