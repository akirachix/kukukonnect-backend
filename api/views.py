from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from sensors.models import SensorData
from .serializers import SensorDataSerializer

class SensorDataAPIView(APIView):
    def get(self, request):
        try:
            sensor_data = SensorData.objects.all()
            serializer = SensorDataSerializer(sensor_data, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def post(self, request):
        serializer = SensorDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    
