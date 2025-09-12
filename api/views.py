from rest_framework.views import APIView
from rest_framework import viewsets
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
from django.http import JsonResponse
from django.utils import timezone
import json
from sensors.models import SensorData
from devices.models import MCU
from devices.mqtt_service import mqtt_client
from .serializers import (
    ThresholdSerializer, UserSerializer, SignupSerializer, LoginSerializer,
    ForgotPasswordSerializer, ResetPasswordSerializer, VerifyCodeSerializer, SetPasswordSerializer,SensorDataSerializer
)
User = get_user_model()
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    

class ThresholdViewSet(viewsets.ViewSet):
    def list(self, request):
        mcus = MCU.objects.all()
        serializer = ThresholdSerializer(mcus, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        mcu = get_object_or_404(MCU, device_id=pk)
        serializer = ThresholdSerializer(mcu)
        return Response(serializer.data)

    def update(self, request, pk=None):
        mcu = get_object_or_404(MCU, device_id=pk)
        serializer = ThresholdSerializer(mcu, data=request.data, partial=True)
        if serializer.is_valid():
            user_id = request.data.get('user_id', None)
            if user_id:
                mcu.user_id_id = user_id
            elif user_id in ('', None):
                mcu.user_id = None
            serializer.save()
            mqtt_client.publish_thresholds(
                mcu.device_id,
                float(mcu.temp_threshold_min),
                float(mcu.temp_threshold_max),
                float(mcu.humidity_threshold_min),
                float(mcu.humidity_threshold_max),
            )
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        return Response(
            {"detail": "POST method not allowed; use PUT or PATCH to update."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def destroy(self, request, *args, **kwargs):
        return Response(
            {"detail": "DELETE method not allowed."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )


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
    
class SensorDataViewset(viewsets.ViewSet):
    queryset = SensorData.objects.all().order_by('-timestamp')

    def list(self, request):
        serializer = SensorDataSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        try:
            data = request.data
            dt = timezone.now()
            
            mcu_instance = MCU.objects.get(device_id=data['device_id'])

            sensor_record = SensorData.objects.create(
                temperature=data['temperature'],
                humidity=data['humidity'],
                device_id=mcu_instance,  
                timestamp=dt
            )
            serializer = SensorDataSerializer(sensor_record)
            return Response({
                'status': 'success',
                'message': 'Sensor data recorded',
                'data': serializer.data,
            }, status=status.HTTP_201_CREATED)

        except MCU.DoesNotExist:
            return Response({'error': 'Invalid device_id, MCU device not found'}, status=status.HTTP_400_BAD_REQUEST)
        except KeyError as e:
            return Response({'error': f'Missing field: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
