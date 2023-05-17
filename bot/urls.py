from django.urls import path
from . import views

urlpatterns = [
    path('verify', views.VerificationCodeView.as_view(), name='verify'),
]
