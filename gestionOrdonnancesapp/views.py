from django.shortcuts import render
from gestionOrdonnancesapp.models import User,Role
from rest_framework.parsers import JSONParser
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login
from rest_framework.permissions import AllowAny, IsAuthenticated
from gestionOrdonnancesapp.serializers import UserSerializer, CustomTokenObtainPairSerializer,RoleSerializer
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.decorators import api_view
from rest_framework_simplejwt.views import TokenObtainPairView
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
import logging
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
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
    def delete(self, request, id):
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        user.delete()
        return Response({'message': 'User deleted successfully'}, status=status.HTTP_200_OK)