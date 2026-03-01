from django.utils import timezone
from .models import CustomUser
from django.http import Http404
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

class AdminAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.path.startswith("/admin") or request.path.startswith("/dashboard"):
            if not request.user.is_authenticated or not request.user.is_superuser:
                raise Http404()

        return self.get_response(request)