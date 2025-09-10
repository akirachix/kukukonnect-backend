from django.test import TestCase
from .models import MCU
from decimal import Decimal
from django.contrib.auth import get_user_model

User = get_user_model()

class MCUTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            phone_number='1234567890'  
        )

        MCU.objects.create(
            device_id="TestDevice001",
            user_id=self.user,
            temp_threshold_min=Decimal('22.00'),
            temp_threshold_max=Decimal('24.00'),
            humidity_threshold_min=Decimal('50.00'),
            humidity_threshold_max=Decimal('70.00')
        )
        self.mcu = MCU.objects.get(temp_threshold_min=Decimal('22.00'))

    def test_mcu_creation(self):
        self.assertEqual(self.mcu.device_type, 'chickens')
        self.assertEqual(self.mcu.temp_threshold_min, Decimal('22.00'))
        self.assertEqual(self.mcu.temp_threshold_max, Decimal('24.00'))
        self.assertEqual(self.mcu.humidity_threshold_min, Decimal('50.00'))
        self.assertEqual(self.mcu.humidity_threshold_max, Decimal('70.00'))
        self.assertEqual(self.mcu.user_id, self.user)
