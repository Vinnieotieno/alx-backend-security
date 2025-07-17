from django.utils.timezone import now
from .models import RequestLog
from django.http import HttpResponseForbidden
from .models import BlockedIP
from ipgeolocation import IpGeolocationAPI
from django.core.cache import cache


class IPTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = request.META.get('REMOTE_ADDR')
        path = request.path
        timestamp = now()

        RequestLog.objects.create(ip_address=ip, path=path, timestamp=timestamp)
        return self.get_response(request)

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = request.META.get('REMOTE_ADDR')

        if BlockedIP.objects.filter(ip_address=ip).exists():
            return HttpResponseForbidden("Your IP has been blocked.")

        # Log request as before
        return self.get_response(request)
    
    api_key = ''
ip_geo = IpGeolocationAPI(api_key)

def get_geolocation(ip):
    cache_key = f"geo_{ip}"
    data = cache.get(cache_key)
    if not data:
        geo = ip_geo.get_geolocation(ip)
        data = {
            "country": geo.get("country_name"),
            "city": geo.get("city")
        }
        cache.set(cache_key, data, timeout=86400)  # cache for 24h
    return data

# In __call__
geo = get_geolocation(ip)
RequestLog.objects.create(
    ip_address=ip,
    path=request.path,
    timestamp=now(),
    country=geo["country"],
    city=geo["city"]
)
