from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import AccessToken
from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache
from users.models import User
import random
from .serializers import (
    UserSerializer, SignupSerializer, LoginSerializer, 
    ForgotPasswordSerializer, ResetPasswordSerializer, VerifyCodeSerializer,SetPasswordSerializer
)

class UserAPIView(generics.GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        users = User.objects.all()
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
        if user.user_type == 'Farmer' and user.email:
            set_password_link = f'https://kukukonnect-frontend.vercel.app/set-password?email={user.email}'
            farmer_name = user.first_name or user.username or "Farmer"
            send_mail(
                "Welcome to Kukukonnect",
                f"Welcome to Kukukonnect {farmer_name}!\nSet your password: {set_password_link}",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            return Response({"message": "Registration successful. Set your password via the link sent to your email."}, status=status.HTTP_201_CREATED)
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