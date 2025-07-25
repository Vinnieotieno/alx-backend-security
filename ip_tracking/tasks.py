
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import RequestLog, SuspiciousIP

@shared_task
def detect_anomalies():
    now = timezone.now()
    one_hour_ago = now - timedelta(hours=1)
    logs = RequestLog.objects.filter(timestamp__gte=one_hour_ago)

    ip_counts = {}
    for log in logs:
        ip_counts[log.ip_address] = ip_counts.get(log.ip_address, 0) + 1

        if log.path in ["/admin", "/login"]:
            SuspiciousIP.objects.get_or_create(
                ip_address=log.ip_address,
                reason="Accessed sensitive path"
            )

    for ip, count in ip_counts.items():
        if count > 100:
            SuspiciousIP.objects.get_or_create(
                ip_address=ip,
                reason="More than 100 requests/hour"
            )
