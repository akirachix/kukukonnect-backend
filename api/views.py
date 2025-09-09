from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from sensors.models import SensorData

class SensorDataAPIView(APIView):
    def get(self, request):
        try:
            sensor_data = SensorData.objects.all().values(
                'sensor_data_id',
                # 'device_id',  
                'temperature',
                'humidity',
                'timestamp'
            )
            return Response(list(sensor_data), status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# Create your views here.


