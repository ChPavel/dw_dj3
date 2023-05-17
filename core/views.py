from typing import Any
from django.contrib.auth import authenticate, login, logout
from rest_framework import status
from rest_framework.generics import GenericAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed
from core.models import User
from core.serializers import CreateUserSerializer, ProfileSerializer, LoginSerializer, UpdatePasswordSerializer


class SignUpView(GenericAPIView):
    """Создание пользователя"""

    serializer_class = CreateUserSerializer

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer: Serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.create_user(**serializer.data)

        return Response(ProfileSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(GenericAPIView):
    """Авторизация пользователя"""

    serializer_class = LoginSerializer

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer: Serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            username=serializer.validated_data['username'], password=serializer.validated_data['password']
        )
        if not user:
            raise AuthenticationFailed

        login(request=request, user=user)

        return Response(ProfileSerializer(user).data)


class ProfileView(RetrieveUpdateDestroyAPIView):
    """Профиль пользователя (получение, удаление)"""

    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self) -> dict:
        return self.request.user

    def delete(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UpdatePasswordView(GenericAPIView):
    """Обновление пароля пользователя"""

    serializer_class = UpdatePasswordSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer: Serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user: User = request.user

        if not user.check_password(serializer.validated_data['old_password']):
            raise AuthenticationFailed('Current password is incorrect')

        user.set_password(serializer.validated_data['new_password'])
        user.save(update_fields=['password'])

        return Response(serializer.data)
