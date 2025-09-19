from rest_framework import serializers
from users.models import User, USER_TYPE_CHOICES
from django.core.cache import cache
from rest_framework.validators import UniqueValidator
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
from sensors.models import SensorData
from devices.models import MCU
import random
import os


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    image = serializers.ImageField(required=False, allow_null=True)
    device_id = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            "id", "username", "first_name", "last_name", "phone_number", "email",
            "password", "user_type", "image", "date_joined", "device_id"
        ]
        read_only_fields = ["id", "date_joined"]

    def validate(self, attrs):
        user_type = attrs.get('user_type')
        device_id = attrs.get('device_id')

        
        if user_type == 'Farmer' and (not device_id or device_id.strip() == ''):
            raise serializers.ValidationError({
                'device_id': 'This field is required for Farmer users.'
            })
    
        if device_id and not MCU.objects.filter(device_id=device_id).exists():
            raise serializers.ValidationError({
                'device_id': f"The device ID '{device_id}' does not exist."
            })

        return attrs

    def create(self, validated_data):
        device_id_str = validated_data.pop('device_id', None)
        if device_id_str:
            validated_data['device_id'] = MCU.objects.get(device_id=device_id_str)
        else:
            validated_data['device_id'] = None

        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()

        if user.user_type == 'Farmer' and user.email:
            set_password_base = os.getenv('SET_PASSWORD_LINK')
            if not set_password_base:
                raise Exception('SET_PASSWORD_LINK environment variable is not set.')
            set_password_link = set_password_base + user.email
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
    device_id = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    class Meta:
        model = User
        fields = [
            "id", "username", "first_name", "last_name", "phone_number", "email",
            "password", "user_type", "image", "date_joined", "device_id"
        ]
        read_only_fields = ["id", "date_joined"]

    def validate(self, attrs):
        user_type = attrs.get('user_type')
        device_id = attrs.get('device_id')

        if user_type == 'Farmer' and (not device_id or device_id.strip() == ''):
            raise serializers.ValidationError({
                'device_id': 'This field is required for Farmer users.'
            })

        if device_id and not MCU.objects.filter(device_id=device_id).exists():
            raise serializers.ValidationError({
                'device_id': f"The device ID '{device_id}' does not exist."
            })

        return attrs

    def create(self, validated_data):
        device_id_str = validated_data.pop('device_id', None)
        if device_id_str:
            validated_data['device_id'] = MCU.objects.get(device_id=device_id_str)
        else:
            validated_data['device_id'] = None

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
            set_password_base = os.getenv('SET_PASSWORD_LINK')
            if not set_password_base:
                raise Exception('SET_PASSWORD_LINK environment variable is not set.')
            set_password_link = set_password_base + user.email
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
    def validate(self, data):
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
    
class ThresholdSerializer(serializers.ModelSerializer):
    class Meta:
        model = MCU
        fields = [
            'device_id',
            'temp_threshold_min',
            'temp_threshold_max',
            'humidity_threshold_min',
            'humidity_threshold_max'
        ]
        extra_kwargs = {
            'humidity_threshold_min': {'required': False, 'allow_null': True},
            'humidity_threshold_max': {'required': False, 'allow_null': True}
        }

class SensorDataSerializer(serializers.ModelSerializer):
    device_id = serializers.CharField(source='device_id.device_id', read_only=True)

    class Meta:
        model = SensorData
        fields = ['sensor_data_id', 'temperature', 'humidity', 'timestamp', 'device_id']
        read_only_fields = ['sensor_data_id', 'timestamp']