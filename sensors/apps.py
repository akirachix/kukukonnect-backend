import os
from django.apps import AppConfig


class SensorsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sensors'
    def ready(self):
        if os.environ.get('RUN_MAIN'):
            from . import mqtt_client
            mqtt_client.start_mqtt()
    