# ip_tracking/middleware.py

from django.http import HttpResponseForbidden
from .models import BlockedIP, RequestLog
from ipgeolocation import IpGeolocationAPI
from django.core.cache import cache
import logging

geo = IpGeolocationAPI("free")  # works for development

class IPTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = self.get_client_ip(request)
        path = request.path

        # Blocked IP
        if BlockedIP.objects.filter(ip_address=ip).exists():
            return HttpResponseForbidden("Your IP is blacklisted.")

        # Check cache
        geo_data = cache.get(ip)
        if not geo_data:
            try:
                response = geo.get_geolocation_data()
                geo_data = {
                    "country": response.get("country_name", ""),
                    "city": response.get("city", "")
                }
                cache.set(ip, geo_data, 60 * 60 * 24)
            except Exception:
                geo_data = {"country": "", "city": ""}

        RequestLog.objects.create(
            ip_address=ip,
            path=path,
            country=geo_data["country"],
            city=geo_data["city"]
        )

        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded:
            return x_forwarded.split(",")[0]
        return request.META.get("REMOTE_ADDR")
