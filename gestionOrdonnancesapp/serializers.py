from rest_framework import serializers
from gestionOrdonnancesapp.models import User, Role, Ordonnance, Allergie, DossierMedicale,Effet, Medicament, MedicamentOrdonnance
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
#from gestion.models import Patient
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['email'] = user.email
        token['role'] = user.role_id

        return token
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'
class UserSerializer(serializers.ModelSerializer):
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all())
    class Meta:
        model = User
        fields = '__all__'
class AllergieSerializer(serializers.ModelSerializer):
    class Meta:
        model=Allergie
        fields = '__all__'
class OrdonnanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ordonnance
        fields = ['id', 'code', 'dossierMedicale']
        
class DossierMedicaleSerializer(serializers.ModelSerializer):
    patient=serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    allergies=serializers.PrimaryKeyRelatedField(queryset=Allergie.objects.all(), many=True)
    class Meta:
        model=DossierMedicale
        fields = '__all__'

class EffetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Effet
        fields = ['id', 'code', 'description', 'gravite']

class MedicamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicament
        fields = ['id', 'code', 'nom', 'description', 'prix', 'disponibilite', 'voie_administration', 'duree_traitement']

class MedicamentOrdonnanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicamentOrdonnance
        fields = ['id', 'ordonnance', 'medicament', 'posologie']