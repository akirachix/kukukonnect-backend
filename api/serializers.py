from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from users.models import User, USER_TYPE_CHOICES
import re

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
        import random
        from django.core.mail import send_mail
        from django.conf import settings
        request = self.context.get('request')
        user_type = validated_data.get('user_type')
        password = validated_data.pop('password', None)

       
        otp = str(random.randint(100000, 999999))
        validated_data['otp'] = otp

        if user_type == 'Farmer':
            if not request or not request.user.is_authenticated or request.user.user_type != 'Agrovet':
                raise serializers.ValidationError('Only an agrovet can create a farmer.')

        if not password and user_type != 'Farmer':
            raise serializers.ValidationError('Password is required.')

        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()

       
        branded_sender = 'Kukukonnect <no-reply@kukukonnect.com>'
        if user.email:
            if user.user_type == 'Agrovet':
                send_mail(
                    subject='Welcome to Kukukonnect',
                    message=f'We are glad to have you onboard! Your OTP is: {otp}',
                    from_email=branded_sender,
                    recipient_list=[user.email],
                    fail_silently=True
                )
            elif user.user_type == 'Farmer':
                set_password_link = f'https://kukukonnect.com/set-password?email={user.email}'
                verify_otp_link = f'https://kukukonnect.com/verify-otp?email={user.email}'
                send_mail(
                    subject='Welcome to Kukukonnect - OTP & Setup',
                    message=(
                        f'Welcome to Kukukonnect!\n'
                        f'Your OTP is: {otp}\n'
                        f'Set your password: {set_password_link}\n'
                        f'Verify your OTP: {verify_otp_link}\n'
                    ),
                    from_email=branded_sender,
                    recipient_list=[user.email],
                    fail_silently=True
                )

        return user
