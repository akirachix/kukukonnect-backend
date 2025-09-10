from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.reverse import reverse
from devices.models import MCU
from .serializers import ThresholdSerializer
from devices.mqtt_service import mqtt_client
from django.shortcuts import get_object_or_404


class APIRootView(APIView):
    def get(self, request, format=None):
        return Response({
            "thresholds": reverse('thresholds-detail', args=["<device_id>"], request=request),
        })


class ThresholdView(APIView):
    def get(self, request, mcu_device_id=None):
        mcu = get_object_or_404(MCU, device_id=mcu_device_id)
        serializer = ThresholdSerializer(mcu)
        return Response(serializer.data)
api/urls.py
    def put(self, request, mcu_device_id=None):
        mcu = get_object_or_404(MCU, device_id=mcu_device_id)
        serializer = ThresholdSerializer(mcu, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            mqtt_client.publish_thresholds(
                mcu.device_id,
                float(mcu.temp_threshold_min),
                float(mcu.temp_threshold_max),
                float(mcu.humidity_threshold_min),
                float(mcu.humidity_threshold_max)
            )
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

