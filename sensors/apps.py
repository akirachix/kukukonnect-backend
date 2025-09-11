from django.apps import AppConfig
import os


class SensorsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sensors'
    def ready(self):
     if os.environ.get('RUN_MAIN'):
        from . import mqtt_service
        mqtt_service.start_mqtt()