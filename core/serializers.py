from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.models import User
from todolist.fields import PasswordField


class ProfileSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя"""

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')


class CreateUserSerializer(serializers.ModelSerializer):
    """Сериализатор создания пользователя"""

    password = PasswordField(required=True, write_only=False)
    password_repeat = PasswordField(required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'password', 'password_repeat')

    def validate(self, attrs: dict) -> dict:
        if attrs['password'] != attrs['password_repeat']:
            raise ValidationError('Passwords must match')
        return attrs


class LoginSerializer(serializers.Serializer):
    """Сериализатор авторизации пользователя"""

    username = serializers.CharField(required=True)
    password = PasswordField(required=True)


class UpdatePasswordSerializer(serializers.Serializer):
    """Сериализатор смены пароля пользователя"""

    old_password = PasswordField(required=True)
    new_password = PasswordField(required=True)
