from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from users.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from .models import User

class FarmerCreationPermissionTest(TestCase):
	def setUp(self):
		self.client = APIClient()
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
			"phone_number": "0700000002"
		}

	def test_agrovet_can_create_farmer(self):
		self.client.force_authenticate(user=self.agrovet)
		url = reverse('user-list')
		response = self.client.post(url, self.farmer_data, format='json')
		self.assertEqual(response.status_code, 201)

	def test_non_agrovet_cannot_create_farmer(self):
		non_agrovet = User.objects.create(
			username="otheruser",
			email="other@example.com",
			user_type="Farmer",
			phone_number="0700000003"
		)
		non_agrovet.set_password("otherpass")
		non_agrovet.save()
		self.client.force_authenticate(user=non_agrovet)
		url = reverse('user-list')
		response = self.client.post(url, self.farmer_data, format='json')
		self.assertEqual(response.status_code, 403)


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
		self.user.otp = '12345'
		self.user.save()
		url = reverse('verify-otp')
		response = self.client.post(url, {'email': self.user.email, 'otp': '12345'}, format='json')
		self.assertEqual(response.status_code, 200)
		self.user.refresh_from_db()
		self.assertIsNone(self.user.otp)

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
		self.user.set_password('oldpassword123!')
		self.user.save()
		url = reverse('reset-password')
		response = self.client.post(url, {
			'email': self.user.email,
			'old_password': 'oldpassword123!',
			'new_password': 'newpassword456!',
			'confirm_password': 'newpassword456!'
		}, format='json')
		self.assertEqual(response.status_code, 200)
		self.user.refresh_from_db()
		self.assertTrue(self.user.check_password('newpassword456!'))
