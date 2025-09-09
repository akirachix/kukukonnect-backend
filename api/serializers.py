from rest_framework import serializers
from sensors.models import SensorData

class SensorDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorData
        fields = ['sensor_data_id', 'temperature', 'humidity', 'timestamp']
