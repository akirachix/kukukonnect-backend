from rest_framework import serializers
from devices.models import MCU

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
            'humidity_threshold_max': {'required': False, 'allow_null': True},
        }

