from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from devices.models import MCU
from .serializers import ThresholdSerializer, DeviceNameSerializer
from devices.mqtt_service import mqtt_client
from django.shortcuts import get_object_or_404

class ThresholdView(APIView):
    def get(self, request, mcu_device_id=None):
        mcu = get_object_or_404(MCU, device_id=mcu_device_id)
        return Response({
            "temp_threshold_min": mcu.temp_threshold_min,
            "temp_threshold_max": mcu.temp_threshold_max,
            "humidity_threshold_min": mcu.humidity_threshold_min,
            "humidity_threshold_max": mcu.humidity_threshold_max,
            "device_name": mcu.device_name,
        })

    def put(self, request, mcu_device_id=None):
        mcu = get_object_or_404(MCU, device_id=mcu_device_id)
        serializer = ThresholdSerializer(mcu, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            mqtt_client.publish_thresholds(
                mcu_device_id,
                float(mcu.temp_threshold_min),
                float(mcu.temp_threshold_max),
                float(mcu.humidity_threshold_min),
                float(mcu.humidity_threshold_max)
            )
            return Response({"status": "published"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeviceNameView(APIView):
    def get(self, request, mcu_device_id=None):
        mcu = get_object_or_404(MCU, device_id=mcu_device_id)
        return Response({"device_name": mcu.device_name})

    def put(self, request, mcu_device_id=None):
        mcu = get_object_or_404(MCU, device_id=mcu_device_id)
        serializer = DeviceNameSerializer(mcu, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "updated"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)