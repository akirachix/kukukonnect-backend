from rest_framework import status, viewsets
from rest_framework.response import Response
from django.core.mail import send_mail
from django.core.cache import cache
from users.models import User
from .serializers import UserSerializer, generate_otp
from users.permissions import IsAgrovetCreatingFarmer
from rest_framework_simplejwt.tokens import RefreshToken
import random
import re


class UserViewSet(viewsets.ModelViewSet):
    def list_users(self, request):
        users = User.objects.all()
        data = [
            {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'phone_number': user.phone_number,
                'user_type': user.user_type,
            }
            for user in users
        ]
        return Response({'users': data}, status=status.HTTP_200_OK)
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            user_type = None
            if self.request.method == 'POST':
                user_type = self.request.data.get('user_type')
            if user_type == 'Farmer':
                return [IsAgrovetCreatingFarmer()]
            return []
        return super().get_permissions()

    def forgot_password(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'detail': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        otp = generate_otp()
        
        send_mail(
            subject='Kukukonnect Password Reset OTP',
            message=f'Your OTP for password reset is: {otp}',
            from_email='queencarineh@gmail.com',
            recipient_list=[user.email],
            fail_silently=True
        )
        cache.set(f"otp_verified_{email}", False, timeout=600)
        cache.set(f"otp_{email}", otp, timeout=600)
        return Response({'detail': 'OTP sent to your email.'}, status=status.HTTP_200_OK)

    def verify_otp(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        if not email or not otp:
            return Response({'detail': 'Email and OTP are required.'}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        stored_otp = cache.get(f"otp_{email}")

       
        if stored_otp is not None:
            stored_otp = str(stored_otp).strip()
        if otp is not None:
            otp = str(otp).strip()
        if cache.get(f"otp_verified_{email}") is None:
            return Response({'detail': 'No OTP request found.'}, status=status.HTTP_404_NOT_FOUND)
        if stored_otp != otp:
            return Response({'detail': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)
        cache.set(f"otp_verified_{email}", True, timeout=600)
        return Response({'detail': 'OTP verified successfully.'}, status=status.HTTP_200_OK)

    def reset_password(self, request):
        email = request.data.get('email')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        if not email or not new_password or not confirm_password:
            return Response({'detail': 'Email, new password, and confirm password are required.'}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        if not cache.get(f"otp_verified_{email}"):
            return Response({'detail': 'OTP must be verified before resetting password.'}, status=status.HTTP_403_FORBIDDEN)
        if new_password != confirm_password:
            return Response({'detail': 'New password and confirm password do not match.'}, status=status.HTTP_400_BAD_REQUEST)
        if not self._validate_password(new_password):
            return Response({'detail': 'Password must be at least 8 characters long and contain letters, numbers, and special characters.'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        cache.set(f"otp_verified_{email}", False, timeout=600)
        return Response({'detail': 'Password reset successful.'}, status=status.HTTP_200_OK)

    def set_password(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')
        if not email or not password or not confirm_password:
            return Response({'detail': 'Email, password, and confirm password are required.'}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        if password != confirm_password:
            return Response({'detail': 'Password and confirm password do not match.'}, status=status.HTTP_400_BAD_REQUEST)
        if not self._validate_password(password):
            return Response({'detail': 'Password must be at least 8 characters long and contain letters, numbers, and special characters.'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(password)
        user.save()
        return Response({'detail': 'Password set successfully.'}, status=status.HTTP_200_OK)

    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = User.objects.filter(email=email).first()
        if not user or not user.check_password(password):
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        refresh = RefreshToken.for_user(user)
        return Response({'token': str(refresh.access_token)}, status=status.HTTP_200_OK)

    def _validate_password(self, password):
        return (
            len(password) >= 8 and
            re.search(r'[A-Za-z]', password) and
            re.search(r'\d', password) and
            re.search(r'[^A-Za-z0-9]', password)
        )
