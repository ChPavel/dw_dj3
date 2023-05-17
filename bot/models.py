from django.db import models
from uuid import uuid4
from core.models import User


class TgUser(models.Model):
    chat_id = models.BigIntegerField(unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, default=None)
    verification_code = models.CharField(max_length=100, null=True, blank=True, default=None)

    @staticmethod
    def generate_verification_code() -> str:
        return str(uuid4())
