from django.shortcuts import render
from apps.user.models import User

def home_page(request):
    users = User.objects.all()
    context = {
        'users': users
    }
    return render(request, 'base/index.html', context)