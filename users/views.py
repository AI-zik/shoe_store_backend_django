from django.shortcuts import get_object_or_404, render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from shoes.utils import get_user_tokens
from .permissions import IsCurrentUserOrAdmin
from .models import User
from .serializers import LoginUserSerializer, PasswordChangeSerializer, RegisterUserSerializer, UpdateUserSerializer, UserDetailSerializer, UserListSerializer

# Create your views here.


class UserTokenCreateView(APIView):

    permission_classes = [AllowAny]
    def post(self, request, format=None):
        serializer = LoginUserSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.get(email = serializer.data['email'])
            tokens = get_user_tokens(user)
            return Response(tokens)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListView(APIView):

    permission_classes = [AllowAny]

    def get(self, request, format=None):
        users = User.objects.all()
        serializer = UserListSerializer(users, many=True)
        return Response(serializer.data)

class UserDetailView(APIView):

    permission_classes = [IsCurrentUserOrAdmin]

    def get_object(self, user_id):
        obj =  get_object_or_404(User, id = user_id)
        self.check_object_permissions(self.request, obj)
        return obj 

    def get(self, request, user_id,format=None):

        user = self.get_object(user_id)
        print(user)
        serializer = UserDetailSerializer(user)
        return Response(serializer.data)

class UserRegisterView(APIView):

    permission_classes = [AllowAny]

    def post(self, request, format=None):
        request.data["user_type"] = 2
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = serializer.data.copy()
            user = User.objects.get(email = serializer.data['email'])
            tokens = get_user_tokens(user)
            data.update(tokens)
            return Response(data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserUpdateView(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, user_id):
        obj =  get_object_or_404(User, id = user_id)
        self.check_object_permissions(self.request, obj)
        return obj

    def put(self, request, user_id, format=None):
        user = self.get_object(user_id)

        if request.user.user_type != 1 and request.user.id != user_id:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = UpdateUserSerializer(user, data=request.data, partial=True, context = {"request" : request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserChangePasswordView(APIView):

    def get_object(self, user_id):
        obj =  get_object_or_404(User, id = user_id)
        self.check_object_permissions(self.request, obj)
        return obj

    def put(self, request, user_id, format=None):
        user = self.get_object(user_id)

        if request.user.user_type != 1 and request.user.id != user_id:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = PasswordChangeSerializer(user, data=request.data, context = {"request" : request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)