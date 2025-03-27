from django.shortcuts import render
from gestionOrdonnancesapp.models import User,Role, Ordonnance, DossierMedicale, Allergie,MedicamentOrdonnance
from rest_framework.parsers import JSONParser
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login
from rest_framework.permissions import AllowAny, IsAuthenticated
from gestionOrdonnancesapp.serializers import AllergieSerializer, DossierMedicaleSerializer, UserSerializer, CustomTokenObtainPairSerializer,RoleSerializer,OrdonnanceSerializer,MedicamentOrdonnanceSerializer,MedicamentSerializer,EffetSerializer
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.decorators import api_view
from rest_framework_simplejwt.views import TokenObtainPairView
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.http import JsonResponse
from .models import Medicament, Effet,  User, Medicament, DossierMedicale

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
class LoginViews(APIView):
    permission_classes = [AllowAny] 
    def updateUser(self,request):
        email=request.data.get('email')
        if email is not None :
            user = User.objects.update_or_create(
            defaults={
             'cin' : request.data.get('cin'),
             'firstName' : request.data.get('firstName'),
             'lastName' : request.data.get('lastName'),
             'email' : request.data.get('email'),
             'age' : request.data.get('age'),
             'address' : request.data.get('address'),
            }, 
            email=email
        ) 
        return Response('user updated succesfully',
               200)   

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        if request.data.get('action')== 'login':

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({'error': 'user not found'},400)

            if not check_password(password, user.password):
                return Response({'error': 'Invalid credentials'},400)
            
            serializer = UserSerializer(user)

            if serializer.data['role'] == 2:
                return Response({'error': 'Patient are not allowed to access'}, status=403)
        
            access_token = AccessToken.for_user(user)
            return Response({
            'data': {
            'access_token': str(access_token),
            'user': serializer.data
                }
            })
        else:
            if email is not None :
                user = User.objects.update_or_create(
                defaults={
                'cin' : request.data.get('cin'),
                'firstName' : request.data.get('firstName'),
                'lastName' : request.data.get('lastName'),
                'email' : request.data.get('email'),
                'age' : request.data.get('age'),
                'address' : request.data.get('address'),
                }, 
                email=email
            ) 
            return Response('user updated succesfully',
                200)  
        
    def put(self, request):
        data = request.data.copy()
        role_name = data.get('role')
        email = data.get('email')
        user_id = data.get('user_id')
        user=""

        try:
            role = Role.objects.get(role=role_name)
        except Role.DoesNotExist:
            return Response({'error': f'Role with name {role_name} does not exist.'}, status=404)
        if user_id is not None:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({'error': 'User not found.'}, status=404)

            if email and User.objects.exclude(id=user.id).filter(email=email).exists():
                return Response({'error': 'User with this email already exists.'}, status=400)

        if role_name == "medecin":
            data['is_staff'] = True
            data['is_superuser'] = True

        data['role'] = role.id
        if user_id is not None:
            serializer = UserSerializer(user, data=data, partial=True)
        else:
            serializer = UserSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        role_serializer = RoleSerializer(role)
        role_data = role_serializer.data

        user_data = serializer.data
        user_data['role'] = role_data['id']

        return Response({
            'user': user_data
        }, status=200)
    def get(self, request):
        id = request.query_params.get('id')
        if id is not None:
            try:
                users = User.objects.get(id=id)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=404)
            users_serializer = UserSerializer(users)
            return Response({
                    'users': users_serializer.data,
                },200)
        else:
            users = User.objects.all()
            response_data = []

            for user in users:
                user_serializer = UserSerializer(user)
                response_data.append(user_serializer.data)
            
            return Response({
                    'users': response_data,
                },200)

    def delete(self, request, id=None):
      user_id = request.query_params.get('id')
      try:
        user = User.objects.get(id=user_id)
      except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)
      user.delete()
      return Response("user deleted succesfuly",status=200)
class DossierMedicaleView(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        patientId=request.data.get("patient")
        allergieIds=request.data.get("allergies",[])
        #kan verifiw l'existance dyalhom fl BD
        patient=get_object_or_404(User, id=patientId)
        allergies=Allergie.objects.filter(id__in=allergieIds)

        serializer=DossierMedicaleSerializer(data=request.data)
        if serializer.is_valid():
            dossier=serializer.save(patient=patient)
            dossier.allergies.set(allergies)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def put(self,request,id):
        dossier=get_object_or_404(DossierMedicale,id=id)
        data=request.data.copy()
        data.pop("patient",None)
        allergies_ids=data.pop("allergies",[])
        allergies=Allergie.objects.filter(id__in=allergies_ids)
        serializer=DossierMedicaleSerializer(dossier,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            dossier.allergies.set(allergies)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request,id):
        dossier=get_object_or_404(DossierMedicale,id=id)
        dossier.delete()
        return Response({"message": "Dossier médical supprimé avec succès"}, status=status.HTTP_200_OK)
    
    def get(self, request, id=None):
      if id is not None:
        try:
            dossier = DossierMedicale.objects.get(id=id)
        except DossierMedicale.DoesNotExist:
            return Response({'error': 'Dossier médical non trouvé'}, status=404)

        serializer = DossierMedicaleSerializer(dossier)
        data = dict(serializer.data)  
        data['allergies'] = AllergieSerializer(dossier.allergies.all(), many=True).data

        return Response({'dossier': data}, status=status.HTTP_200_OK)
      else:
        dossiers = DossierMedicale.objects.all()
        serializer = DossierMedicaleSerializer(dossiers, many=True)
        dossiers_data = list(serializer.data)  

        for dossier, data in zip(dossiers, dossiers_data):
            data['allergies'] = AllergieSerializer(dossier.allergies.all(), many=True).data

        return Response({'dossiers': dossiers_data}, status=status.HTTP_200_OK)

        
class AllergieView(APIView):
    permission_classes=[AllowAny]
    def post(self, request):
        print("Requête POST reçue avec les données :", request.data)  
        serializer=AllergieSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def put(self,request,id):
        allergie=get_object_or_404(Allergie,id=id)
        serializer=AllergieSerializer(allergie,data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self,request,id):
        try:
            allergie = Allergie.objects.get(id=id)
        except Allergie.DoesNotExist:
            return Response({'error':'allergie not found'}, status=404)
        allergie.delete()
        return Response("allergie deleted succesfuly",status=200)
    def get(self, request, id=None):
        if id is not None:
            try:
                allergie=Allergie.objects.get(id=id)
            except Allergie.DoesNotExist:
                return Response({'error': 'Allergie not found'}, status=status.HTTP_404_NOT_FOUND)
            serializer=AllergieSerializer(allergie)
            return Response({'allergie':serializer.data},status=status.HTTP_200_OK)
        else:
            allergies=Allergie.objects.all()
            serializer=AllergieSerializer(allergies, many=True)
            return Response({'allergies':serializer.data},status=status.HTTP_200_OK)


class MedicamentInteractionView(APIView):
    permission_classes=[AllowAny]
    def get(self, request, medicament1_id, medicament2_id):
        try:
            medicament1 = get_object_or_404(Medicament, id=medicament1_id)
            medicament2 = get_object_or_404(Medicament, id=medicament2_id)

            effets_communs = Effet.objects.filter(medicaments=medicament1).filter(medicaments=medicament2)

            if effets_communs.exists():
                effets_list = [{"description": effet.description, "gravite": effet.gravite} for effet in effets_communs]
                return Response({
                    "status": "danger",
                    "message": f"Interaction détectée entre {medicament1.nom} et {medicament2.nom}",
                    "effets": effets_list
                }, status=status.HTTP_200_OK)

            return Response({"status": "ok", "message": "Pas d'interaction détectée"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AllergyCheckView(APIView):
    permission_classes=[AllowAny]
    def get(self, request, user_id, medicament_id):
        try:
            user = get_object_or_404(User, id=user_id)
            dossier = get_object_or_404(DossierMedicale, patient=user)
            medicament = get_object_or_404(Medicament, id=medicament_id)

            allergies = dossier.allergies.all()
            for allergie in allergies:
                if allergie.nom.lower() in medicament.molecule_active.lower():
                    return Response({
                        "status": "danger",
                        "message": f"Allergie détectée : {allergie.nom} - Gravité : {allergie.gravite}"
                    }, status=status.HTTP_200_OK)

            return Response({"status": "ok", "message": "Pas d'allergie détectée"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class OrdonnanceView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Créer une nouvelle ordonnance
        serializer = OrdonnanceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, id=None):
        if id:
            # Récupérer une ordonnance spécifique par son ID
            ordonnance = get_object_or_404(Ordonnance, id=id)
            serializer = OrdonnanceSerializer(ordonnance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # Récupérer toutes les ordonnances
            ordonnances = Ordonnance.objects.all()
            serializer = OrdonnanceSerializer(ordonnances, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        # Mettre à jour une ordonnance
        ordonnance = get_object_or_404(Ordonnance, id=id)
        serializer = OrdonnanceSerializer(ordonnance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        # Supprimer une ordonnance
        ordonnance = get_object_or_404(Ordonnance, id=id)
        ordonnance.delete()
        return Response({"message": "Ordonnance supprimée avec succès."}, status=status.HTTP_200_OK)


# ---- EFFET VIEWS ----
class EffetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Créer un effet secondaire
        serializer = EffetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, id=None):
        # Si un ID est fourni, récupérer l'effet secondaire spécifique
        if id is not None:
            effet = get_object_or_404(Effet, id=id)
            serializer = EffetSerializer(effet)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # Sinon, récupérer tous les effets secondaires
        effets = Effet.objects.all()
        serializer = EffetSerializer(effets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        # Modifier un effet secondaire existant
        effet = get_object_or_404(Effet, id=id)
        serializer = EffetSerializer(effet, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        # Supprimer un effet secondaire
        effet = get_object_or_404(Effet, id=id)
        effet.delete()
        return Response({"message": "Effet secondaire supprimé avec succès"}, status=status.HTTP_200_OK)


# ---- MEDICAMENT VIEWS ----
class MedicamentView(APIView):
    permission_classes = [AllowAny]

    # Récupérer la liste de tous les médicaments ou un médicament spécifique par ID
    def get(self, request, id=None):
        if id:  # Si un ID est fourni, on récupère un médicament spécifique
            try:
                medicament = Medicament.objects.get(id=id)
            except Medicament.DoesNotExist:
                return Response({'error': 'Medicament not found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = MedicamentSerializer(medicament)
            return Response({'medicament': serializer.data}, status=status.HTTP_200_OK)
        
        # Si aucun ID, on retourne tous les médicaments
        medicaments = Medicament.objects.all()
        serializer = MedicamentSerializer(medicaments, many=True)
        return Response({'medicaments': serializer.data}, status=status.HTTP_200_OK)

    # Ajouter un nouveau médicament (POST)
    def post(self, request):
        serializer = MedicamentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Mettre à jour un médicament existant (PUT)
    def put(self, request, id):
        medicament = get_object_or_404(Medicament, id=id)
        serializer = MedicamentSerializer(medicament, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Supprimer un médicament (DELETE)
    def delete(self, request, id):
        try:
            medicament = Medicament.objects.get(id=id)
        except Medicament.DoesNotExist:
            return Response({'error': 'Medicament not found'}, status=status.HTTP_404_NOT_FOUND)
        medicament.delete()
        return Response("Medicament deleted successfully", status=status.HTTP_200_OK)


# ---- MEDICAMENTORDONNANCE VIEWS ----
class MedicamentOrdonnanceView(APIView):
    permission_classes = [AllowAny]

    # Méthode POST pour créer un MedicamentOrdonnance
    def post(self, request):
        # Sérialisation des données envoyées
        serializer = MedicamentOrdonnanceSerializer(data=request.data)
        # Vérification de la validité des données
        if serializer.is_valid():
            # Sauvegarde dans la base de données
            serializer.save()
            # Retour d'une réponse avec le code 201 et les données créées
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # Retour d'une erreur si les données sont invalides
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Méthode PUT pour mettre à jour un MedicamentOrdonnance
    def put(self, request, id):
        # Récupération du MedicamentOrdonnance par son ID
        medicament_ordonnance = get_object_or_404(MedicamentOrdonnance, id=id)
        # Sérialisation avec les données envoyées (et autorisation de modification partielle)
        serializer = MedicamentOrdonnanceSerializer(medicament_ordonnance, data=request.data, partial=True)
        # Vérification de la validité des données
        if serializer.is_valid():
            # Sauvegarde des nouvelles données
            serializer.save()
            # Retour des données mises à jour avec le code 200
            return Response(serializer.data, status=status.HTTP_200_OK)
        # Retour d'une erreur si les données sont invalides
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Méthode DELETE pour supprimer un MedicamentOrdonnance
    def delete(self, request, id):
        try:
            # Récupération du MedicamentOrdonnance par son ID
            medicament_ordonnance = MedicamentOrdonnance.objects.get(id=id)
        except MedicamentOrdonnance.DoesNotExist:
            # Si l'objet n'existe pas, renvoyer une erreur 404
            return Response({'error': 'MedicamentOrdonnance not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Suppression de l'objet
        medicament_ordonnance.delete()
        # Retourner une confirmation de suppression
        return Response("MedicamentOrdonnance deleted successfully", status=status.HTTP_200_OK)

    # Méthode GET pour récupérer des MedicamentOrdonnances
    def get(self, request, id=None):
        if id is not None:
            try:
                # Récupérer un MedicamentOrdonnance spécifique
                medicament_ordonnance = MedicamentOrdonnance.objects.get(id=id)
            except MedicamentOrdonnance.DoesNotExist:
                # Si l'objet n'existe pas, retourner une erreur 404
                return Response({'error': 'MedicamentOrdonnance not found'}, status=status.HTTP_404_NOT_FOUND)
            # Sérialiser les données de l'objet récupéré
            serializer = MedicamentOrdonnanceSerializer(medicament_ordonnance)
            # Retourner l'objet avec le code 200
            return Response({'medicament_ordonnance': serializer.data}, status=status.HTTP_200_OK)
        else:
            # Si aucun paramètre 'id' n'est donné, récupérer tous les MedicamentOrdonnances
            medicament_ordonnances = MedicamentOrdonnance.objects.all()
            # Sérialiser tous les objets
            serializer = MedicamentOrdonnanceSerializer(medicament_ordonnances, many=True)
            # Retourner tous les objets avec le code 200
            return Response({'medicament_ordonnances': serializer.data}, status=status.HTTP_200_OK)