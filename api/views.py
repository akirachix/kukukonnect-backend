from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.reverse import reverse
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import AccessToken
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import get_user_model
import random

from devices.models import MCU
from devices.mqtt_service import mqtt_client
from .serializers import (
    ThresholdSerializer, UserSerializer, SignupSerializer, LoginSerializer,
    ForgotPasswordSerializer, ResetPasswordSerializer, VerifyCodeSerializer, SetPasswordSerializer
)

User = get_user_model()

class APIRootView(APIView):
    def get(self, request, format=None):
        return Response({
            "thresholds": reverse('thresholds-detail', args=["<device_id>"], request=request),
             "users": reverse('users', request=request)
        })

class ThresholdView(APIView):
    def get(self, request, mcu_device_id=None):
        mcu = get_object_or_404(MCU, device_id=mcu_device_id)
        serializer = ThresholdSerializer(mcu)
        return Response(serializer.data)

    def put(self, request, mcu_device_id=None):
        mcu = get_object_or_404(MCU, device_id=mcu_device_id)
        serializer = ThresholdSerializer(mcu, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            mqtt_client.publish_thresholds(
                mcu.device_id,
                float(mcu.temp_threshold_min),
                float(mcu.temp_threshold_max),
                float(mcu.humidity_threshold_min),
                float(mcu.humidity_threshold_max)
            )
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserAPIView(generics.GenericAPIView):
    queryset = User.objects.all()  
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        users = self.get_queryset() 
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class SetPasswordView(generics.GenericAPIView):
    serializer_class = SetPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password set successfully."})

class SignupView(generics.CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"message": "Registration successful."}, status=status.HTTP_201_CREATED)

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        access = AccessToken.for_user(user)
        return Response({
            "token": str(access)
        })

class ForgotPasswordView(generics.GenericAPIView):
    serializer_class = ForgotPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        user = User.objects.get(email=email)
        otp = random.randint(1000, 9999)
        cache.set(f"otp_{user.id}", otp, timeout=600)
        send_mail(
            "Your OTP Code",
            f"Use this OTP to reset your password: {otp}",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return Response({"message": "OTP sent to your email"})

class VerifyCodeView(generics.GenericAPIView):
    serializer_class = VerifyCodeSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"message": "OTP verified successfully"})

class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password has been reset successfully"})
