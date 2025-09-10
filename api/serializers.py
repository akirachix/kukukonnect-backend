from rest_framework import serializers
from users.models import User, USER_TYPE_CHOICES
from django.core.cache import cache
from rest_framework.validators import UniqueValidator
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
import random

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            "id", "username", "first_name", "last_name", "phone_number", "email",
            "password", "user_type", "image", "date_joined"
        ]
        read_only_fields = ["id", "date_joined"]
    

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        
        if password:
            user.set_password(password)
        user.save()
        
        if user.user_type == 'Farmer' and user.email:
            set_password_link = f'https://kukukonnect-frontend.vercel.app/set-password?email={user.email}'
            send_mail(
                subject='Welcome to Kukukonnect - Set Your Password',
                message=(
                    f'Welcome to Kukukonnect!\n'
                    f'Set your password: {set_password_link}\n'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True
            )
        return user

class SignupSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all(), message="Username already taken.")]
    )
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'},
        required=False
    )
    phone_number = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all(), message="Phone number already registered.")]
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all(), message="Email already registered.")]
    )

    class Meta:
        model = User
        fields = [
            "id", "username", "first_name", "last_name", "phone_number", "email",
            "password", "user_type", "image", "date_joined"
        ]
        read_only_fields = ["id", "date_joined"]

    
    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User(**validated_data)

        if user.user_type == "Agrovet":
            if not password:
                raise serializers.ValidationError({"password": "Password is required for Agrovets."})
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()

        if user.user_type == 'Farmer' and user.email:
            set_password_link = f'https://kukukonnect-frontend.vercel.app/set-password?email={user.email}'
            from django.conf import settings
            send_mail(
                subject='Welcome to Kukukonnect - Set Your Password',
                message=(
                    f'Welcome to Kukukonnect {user.username}!\n'
                    f'Set your password: {set_password_link}\n'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False
            )
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data["email"], password=data["password"])
        if not user:
            raise serializers.ValidationError("Invalid credentials.")
        if not user.is_active:
            raise serializers.ValidationError("This account is inactive.")
        data["user"] = user
        return data   

class SetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match")
        try:
            user = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        if user.user_type != "Farmer":
            raise serializers.ValidationError("Only farmers can set their password using this endpoint.")
        return data

    def save(self, **kwargs):
        user = User.objects.get(email=self.validated_data["email"])
        user.set_password(self.validated_data["password"])
        user.save()
        return user     

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        otp = random.randint(1000, 9999)
        cache.set(f"otp_{user.id}", otp, timeout=600)
        return value

class VerifyCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=4)
    
    def validate(self, data):
        try:
            user = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email")
        cached_otp = cache.get(f"otp_{user.id}")
        if not cached_otp or str(cached_otp) != str(data["otp"]):
            raise serializers.ValidationError("Invalid or expired OTP")
        cache.set(f"otp_verified_{user.id}", True, timeout=600)
        return data


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)
    
    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match")
        try:
            user = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        otp_verified = cache.get(f"otp_verified_{user.id}")
        if not otp_verified:
            raise serializers.ValidationError("OTP not verified. Please verify OTP before resetting password.")
        return data
    
    def save(self, **kwargs):
        user = User.objects.get(email=self.validated_data["email"])
        user.set_password(self.validated_data["password"])
        user.save()
        cache.delete(f"otp_{user.id}")
        cache.delete(f"otp_verified_{user.id}")
        return user

