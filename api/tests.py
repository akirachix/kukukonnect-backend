from django.test import TestCase
from rest_framework.test import APIClient
from devices.models import MCU
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()

class ThresholdAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.test_device_id = "ESP32-TempCtrl-000000000000"
        self.user = User.objects.create_user(username="testuser", password="testpass", phone_number="1234567890")
        self.mcu = MCU.objects.create(
            device_id=self.test_device_id,
            user_id=self.user,
            device_type="chickens",
            temp_threshold_min=Decimal('20.00'),
            temp_threshold_max=Decimal('30.00'),
            humidity_threshold_min=Decimal('40.00'),
            humidity_threshold_max=Decimal('70.00')
        )
    
    def test_get_threshold(self):
        response = self.client.get(f'/api/thresholds/{self.test_device_id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.data['temp_threshold_min']), "20.00")

    def test_put_threshold(self):
        response = self.client.put(
            f'/api/thresholds/{self.test_device_id}/',
            data={
                "temp_threshold_min": 21.00,
                "temp_threshold_max": 29.00,
                "humidity_threshold_min": 45.00,
                "humidity_threshold_max": 65.00
            },
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.mcu.refresh_from_db()
        self.assertEqual(float(self.mcu.temp_threshold_min), 21.0)

