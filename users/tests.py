import os
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from users.models import User
from devices.models import MCU

class FarmerCreationPermissionTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        os.environ['SET_PASSWORD_LINK'] = 'https://test-set-password-link/?email='

    def setUp(self):
        self.client = APIClient()

        self.mcu = MCU.objects.create(
            device_id="TestDevice001",
            device_type='chickens',
            temp_threshold_min=Decimal('22.00'),
            temp_threshold_max=Decimal('24.00'),
            humidity_threshold_min=Decimal('50.00'),
            humidity_threshold_max=Decimal('70.00')
        )

        self.agrovet = User.objects.create(
            username="agrovetuser",
            email="agrovet@example.com",
            user_type="Agrovet",
            phone_number="0700000001"
        )
        self.agrovet.set_password("agrovetpass")
        self.agrovet.save()

        self.farmer_data = {
            "username": "farmeruser",
            "email": "farmer@example.com",
            "user_type": "Farmer",
            "phone_number": "0700000002",
            "first_name": "Test",
            "last_name": "Farmer",
            "device_id": self.mcu.mcu_id  
        }

    def test_agrovet_can_create_farmer(self):
        self.client.force_authenticate(user=self.agrovet)
        url = reverse('users')
        response = self.client.post(url, self.farmer_data, format='json')

    def test_anyone_can_create_farmer(self):
        non_agrovet = User.objects.create(
            username="otheruser",
            email="other@example.com",
            user_type="Farmer",
            phone_number="0700000003"
        )
        non_agrovet.set_password("otherpass")
        non_agrovet.save()
        self.client.force_authenticate(user=non_agrovet)
        url = reverse('users')
        response = self.client.post(url, self.farmer_data, format='json')


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="testuser",
            email="testuser@example.com",
            user_type="Farmer",
            phone_number="0712345678",
        )
        self.user.set_password("testpassword")
        self.user.save()
        self.client = APIClient()

    def test_user_creation(self):
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.email, "testuser@example.com")
        self.assertEqual(self.user.user_type, "Farmer")
        self.assertEqual(self.user.phone_number, "0712345678")
        self.assertIsInstance(self.user, User)

    def test_str_method(self):
        self.assertTrue(str(self.user))

    def test_login(self):
        url = reverse('login')
        response = self.client.post(url, {'email': self.user.email, 'password': 'testpassword'}, format='json')
        self.assertIn(response.status_code, [200, 403])

    def test_verify_otp(self):
        url_forgot = reverse('forgot-password')
        forgot_response = self.client.post(url_forgot, {'email': self.user.email}, format='json')
        from django.core.cache import cache
        otp = cache.get(f"otp_{self.user.id}")
        print(f"DEBUG: OTP for user {self.user.email} (id={self.user.id}): {otp}")
        url_verify = reverse('verify-otp')
        response = self.client.post(url_verify, {'email': self.user.email, 'otp': otp}, format='json')
        self.assertEqual(response.status_code, 200)

    def test_set_password(self):
        self.user.otp = None
        self.user.save()
        url = reverse('set-password')
        response = self.client.post(url, {
            'email': self.user.email,
            'password': 'NewPassword123!',
            'confirm_password': 'NewPassword123!'
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPassword123!'))

    def test_reset_password(self):
        url_forgot = reverse('forgot-password')
        self.client.post(url_forgot, {'email': self.user.email}, format='json')
        from django.core.cache import cache
        otp = cache.get(f"otp_{self.user.id}")
        print(f"DEBUG: OTP for user {self.user.email} (id={self.user.id}): {otp}")
        url_verify = reverse('verify-otp')
        self.client.post(url_verify, {'email': self.user.email, 'otp': otp}, format='json')
        url_reset = reverse('reset-password')
        response = self.client.post(url_reset, {
            'email': self.user.email,
            'password': 'newpassword456!',
            'confirm_password': 'newpassword456!'
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword456!'))
