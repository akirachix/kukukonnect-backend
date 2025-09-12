from django.db import models
from devices.models import MCU

class SensorData(models.Model):
    sensor_data_id = models.AutoField(primary_key=True)
    device_id = models.ForeignKey(MCU, on_delete=models.CASCADE, null=True, blank=True)
    temperature = models.DecimalField(max_digits=5, decimal_places=2)  
    humidity = models.DecimalField(max_digits=5, decimal_places=2)    
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"SensorData {self.sensor_data_id}  at {self.timestamp}"
