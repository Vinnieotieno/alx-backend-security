

from django.http import HttpResponse
from ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='10/m', block=True)
def login_view(request):
    return HttpResponse("Authenticated user login.")

@ratelimit(key='ip', rate='5/m', block=True)
def anonymous_view(request):
    return HttpResponse("Anonymous user login.")
