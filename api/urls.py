from django.urls import path
from .views import ThresholdView, DeviceNameView
from django.http import JsonResponse


urlpatterns = [
    path('thresholds/<str:mcu_device_id>/', ThresholdView.as_view(), name='thresholds'),
    path('device-name/<str:mcu_device_id>/', DeviceNameView.as_view(), name='device-name'),
]
