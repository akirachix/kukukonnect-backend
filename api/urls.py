from django.urls import path
from .views import APIRootView, ThresholdView

urlpatterns = [
    path('', APIRootView.as_view(), name='api-root'),
    path('thresholds/<str:mcu_device_id>/', ThresholdView.as_view(), name='thresholds-detail'),
]

