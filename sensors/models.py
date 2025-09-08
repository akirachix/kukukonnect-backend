from django.db import models
from mcu.models import MCU
class SensorData(models.Model):
    sensor_data_id = models.AutoField(primary_key=True)
    mcu = models.ForeignKey(MCU, on_delete=models.CASCADE, related_name='sensor_data')
    temperature = models.DecimalField(max_digits=5, decimal_places=2)  
    humidity = models.DecimalField(max_digits=5, decimal_places=2)    
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"SensorData {self.sensor_data_id} - MCU {self.mcu.name} at {self.timestamp}"
# Create your models here.
