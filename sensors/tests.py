from django.test import TestCase
from sensors.models import SensorData
from datetime import datetime

class SensorDataModelTest(TestCase):
    def test_create_sensor_data(self):
      
        sensor_data = SensorData.objects.create(
            temperature=23.45,
            humidity=65.20,
            timestamp=datetime(2025, 9, 7, 18, 30, 0)
        )
        self.assertIsInstance(sensor_data, SensorData)
        self.assertEqual(sensor_data.temperature, 23.45)
        self.assertEqual(sensor_data.humidity, 65.20)
        self.assertEqual(sensor_data.timestamp, datetime(2025, 9, 7, 18, 30, 0))

    def test_str_representation(self):
        sensor_data = SensorData.objects.create(
            temperature=23.45,
            humidity=65.20,
            timestamp=datetime(2025, 9, 7, 18, 30, 0)
        )
       
        expected_str = f"SensorData {sensor_data.sensor_data_id} at {sensor_data.timestamp}"
        actual_str = f"SensorData {sensor_data.sensor_data_id} at {sensor_data.timestamp}"
        self.assertEqual(actual_str, expected_str)

