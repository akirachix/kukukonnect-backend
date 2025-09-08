from rest_framework import status, viewsets
from rest_framework.response import Response
from django.core.mail import send_mail
from users.models import User
from .serializers import UserSerializer
from users.permissions import IsAgrovetCreatingFarmer
from rest_framework_simplejwt.tokens import RefreshToken
import random
import re

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAgrovetCreatingFarmer]

   
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = User.objects.filter(email=email).first()

        if not user or not user.check_password(password):
            return Response(
                {'detail': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if user.otp:
            return Response(
                {'detail': 'Please verify your OTP before logging in.'},
                status=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(user)
        return Response(
            {'token': str(refresh.access_token)},
            status=status.HTTP_200_OK
        )

    
    def reset_password(self, request):
        email = request.data.get('email')
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if not email or not old_password or not new_password or not confirm_password:
            return Response(
                {'detail': 'All fields are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.filter(email=email).first()
        if not user:
            return Response(
                {'detail': 'User not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if new_password != confirm_password:
            return Response(
                {'detail': 'New password and confirm password do not match.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.check_password(old_password):
            return Response(
                {'detail': 'Old password is incorrect.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not self._validate_password(new_password):
            return Response(
                {'detail': 'Password must be at least 8 characters long and contain letters, numbers, and special characters.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()
        return Response(
            {'detail': 'Password reset successful.'},
            status=status.HTTP_200_OK
        )

    
    def verify_otp(self, request):
        otp = request.data.get('otp')
        email = request.data.get('email')

        if not email or not otp:
            return Response(
                {'detail': 'Email and OTP are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.filter(email=email).first()
        if not user:
            return Response(
                {'detail': 'User not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if user.otp and str(user.otp).strip() == str(otp).strip():
            user.otp = None
            user.save()
            return Response(
                {'detail': 'OTP verified successfully.'},
                status=status.HTTP_200_OK
            )

        return Response(
            {'detail': 'Invalid OTP.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    
    def set_password(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')

        if not email or not password or not confirm_password:
            return Response(
                {'detail': 'Email, password, and confirm password are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.filter(email=email).first()
        if not user:
            return Response(
                {'detail': 'User not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if user.otp:
            return Response(
                {'detail': 'OTP must be verified before setting password.'},
                status=status.HTTP_403_FORBIDDEN
            )

        if password != confirm_password:
            return Response(
                {'detail': 'Password and confirm password do not match.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not self._validate_password(password):
            return Response(
                {'detail': 'Password must be at least 8 characters long and contain letters, numbers, and special characters.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(password)
        user.save()
        return Response(
            {'detail': 'Password set successfully.'},
            status=status.HTTP_200_OK
        )

    def _validate_password(self, password):
        return (
            len(password) >= 8 and
            re.search(r'[A-Za-z]', password) and
            re.search(r'\d', password) and
            re.search(r'[^A-Za-z0-9]', password)
        )
