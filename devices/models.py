from django.db import models
class MCU(models.Model):
    mcu_id = models.AutoField(primary_key=True)
    device_id = models.CharField(max_length=50, unique=True)
    device_type = models.CharField(
        max_length=20,
        choices=(('chicks', 'Chicks'), ('chickens', 'Chickens')),
        default='chickens'
    )
    temp_threshold_min = models.DecimalField(max_digits=5, decimal_places=2)
    temp_threshold_max = models.DecimalField(max_digits=5, decimal_places=2)
    humidity_threshold_min = models.DecimalField(max_digits=5, decimal_places=2)
    humidity_threshold_max = models.DecimalField(max_digits=5, decimal_places=2)
