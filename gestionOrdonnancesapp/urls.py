from django.urls import path , include
from gestionOrdonnancesapp.views import LoginViews
from . import views

urlpatterns = [
   path('login',LoginViews.as_view()),
]