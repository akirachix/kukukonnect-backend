from rest_framework import serializers

class ThresholdSerializer(serializers.Serializer):
    temp_threshold_min = serializers.DecimalField(max_digits=5, decimal_places=2)
    temp_threshold_max = serializers.DecimalField(max_digits=5, decimal_places=2)
    humidity_threshold_min = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, allow_null=True)
    humidity_threshold_max = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, allow_null=True)

class DeviceNameSerializer(serializers.Serializer):
    device_name = serializers.CharField(max_length=50)
