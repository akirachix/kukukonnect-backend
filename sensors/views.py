from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import RelayStatus
import json

@csrf_exempt
def relay_status_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            relay = RelayStatus.objects.create(
                device_id=data.get("device_id"),
                timestamp=data.get("timestamp"),
                heater_relay=data.get("heater_relay"),
                fan_relay=data.get("fan_relay"),
                system_mode=data.get("system_mode"),
            )
            return JsonResponse({"status": "ok", "received": data})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    else:
        return JsonResponse({"error": "Invalid method"}, status=405)

def publish_message(request):
   
    relays = RelayStatus.objects.order_by('-created_at')[:100]  
    data = [
        {
            "device_id": r.device_id,
            "timestamp": r.timestamp,
            "heater_relay": r.heater_relay,
            "fan_relay": r.fan_relay,
            "system_mode": r.system_mode,
            "created_at": r.created_at.isoformat(),
        }
        for r in relays
    ]
    return JsonResponse({"messages": data})

