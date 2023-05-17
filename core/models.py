from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель пользователя"""

    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    MALE = 'm'
    FEMALE = 'f'
    SEX = [(MALE, 'Male'), (FEMALE, 'Female')]

    ADMIN = 'admin'
    USER = 'user'
    UNKNOWN = 'unknown'
    ROLE = [(ADMIN, ADMIN), (USER, USER), (UNKNOWN, UNKNOWN)]

    sex = models.CharField(max_length=1, choices=SEX, default=MALE)
    role = models.CharField(max_length=8, choices=ROLE, default=UNKNOWN)
