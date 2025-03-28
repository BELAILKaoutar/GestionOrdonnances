from django.urls import path , include
from gestionOrdonnancesapp.views import LoginViews
from . import views

urlpatterns = [
    path('login/', LoginViews.as_view(), name='login'),  # For login functionality (POST, PUT)
    path('login/<int:id>/', LoginViews.as_view(), name='delete_user'),  # For deleting a user (DELETE)
]
