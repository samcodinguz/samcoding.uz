from django.utils import timezone
from .models import CustomUser
from django.shortcuts import redirect

class UpdateLastActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            CustomUser.objects.filter(id=request.user.id).update(last_activity=timezone.now())
        response = self.get_response(request)
        return response

class Redirect401Middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.path.startswith("/accounts/google/login/callback/") and response.status_code == 401:
            return redirect("/")

        return response