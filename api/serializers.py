from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from users.models import User, USER_TYPE_CHOICES
import re
import random

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email',
            'phone_number', 'image', 'user_type', 'password', 'date_joined'
        ]
        read_only_fields = ['id', 'date_joined']

    def validate_username(self, value):
        user_id = self.instance.id if self.instance else None
        qs = User.objects.filter(username=value)
        if user_id:
            qs = qs.exclude(id=user_id)
        if qs.exists():
            raise serializers.ValidationError('Username has already been taken.')
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError('Password must be at least 8 characters long.')
        if not re.search(r'[A-Za-z]', value):
            raise serializers.ValidationError('Password must contain at least one letter.')
        if not re.search(r'\d', value):
            raise serializers.ValidationError('Password must contain at least one number.')
        if not re.search(r'[^A-Za-z0-9]', value):
            raise serializers.ValidationError('Password must contain at least one special character.')
        return value

    def validate_email(self, value):
        if value and not serializers.EmailField().run_validation(value):
            raise serializers.ValidationError('Please enter a valid email address.')
        return value

    def validate_phone_number(self, value):
        phone_regex = r'^(\+\d{1,3})?\d{9,15}$'
        if not re.match(phone_regex, value):
            raise serializers.ValidationError('Please enter a valid phone number.')
        user_id = self.instance.id if self.instance else None
        qs = User.objects.filter(phone_number=value)
        if user_id:
            qs = qs.exclude(id=user_id)
        if qs.exists():
            raise serializers.ValidationError('A user with this phone number already exists.')
        return value

    def create(self, validated_data):
        from django.core.mail import send_mail
        import logging
        logger = logging.getLogger('kukukonnect')
        request = self.context.get('request')
        user_type = validated_data.get('user_type')
        password = validated_data.pop('password', None)

        validated_data.pop('otp', None)

        logger.info(f"CREATE USER: user_type={user_type}, request={request}, request.user={getattr(request, 'user', None)}")

        if user_type == 'Farmer':
            if not request or not request.user.is_authenticated or request.user.user_type != 'Agrovet':
                logger.error(f"Farmer creation blocked: request={request}, request.user={getattr(request, 'user', None)}")
                raise serializers.ValidationError('Only an agrovet can create a farmer.')

        if not password and user_type != 'Farmer':
            logger.error(f"Password required for non-farmer: validated_data={validated_data}")
            raise serializers.ValidationError('Password is required.')

        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()

        logger.info(f"User created: {user}")

        if user.email and user.user_type == 'Farmer':
            set_password_link = f'https://kukukonnect-frontend.vercel.app/set-password?email={user.email}'
            send_mail(
                subject='Welcome to Kukukonnect - Set Your Password',
                message=(
                    f'Welcome to Kukukonnect!\n'
                    f'Set your password: {set_password_link}\n'
                ),
                from_email="queencarineh@gmail.com",
                recipient_list=[user.email],
                fail_silently=True
            )

        return user

def generate_otp():
    return f"{random.randint(0, 9999):04d}"
