from django.db import models
# from mcu.models import MCU
class SensorData(models.Model):
    sensor_data_id = models.AutoField(primary_key=True)
    # mcu = models.ForeignKey(MCU, on_delete=models.CASCADE, related_name='sensor_data')
    temperature = models.DecimalField(max_digits=5, decimal_places=2)  
    humidity = models.DecimalField(max_digits=5, decimal_places=2)    
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"SensorData {self.sensor_data_id} - MCU {self.mcu.name} at {self.timestamp}"
class RelayStatus(models.Model):
    device_id = models.CharField(max_length=100)
    timestamp = models.BigIntegerField()
    heater_relay = models.BooleanField()
    fan_relay = models.BooleanField()
    system_mode = models.CharField(max_length=50)
    temperature = models.FloatField(null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device_id} @ {self.timestamp}"