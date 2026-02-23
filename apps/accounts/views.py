from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from apps.core.utils import get_base_context
from .models import CustomUser
from . import utils

def sign_in(request):
    if request.user.is_authenticated:
        return redirect("index")
    
    if request.method == "POST":
        username = request.POST.get("username").strip()
        password = request.POST.get("password").strip()
        remember = request.POST.get("rememberme")

        if not username or not password:
            messages.error(request, "Iltimos, barcha maydonlarni to'ldiring!")
            return redirect("sign-in")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            if not remember:
                request.session.set_expiry(0)
            messages.success(request, "Tizimga muvaffaqiyatli kirdingiz!")
            return redirect("index")
        
        messages.error(request, "Kechirasiz, bunday foydalanuvchi topilmadi!")
        return redirect("sign-in")

    context = {
        **get_base_context(request),
        'title': 'Kirish',
    }

    return render(request, 'accounts/sign-in.html', context)

def sign_up(request):
    if request.user.is_authenticated:
        return redirect("index")
    
    if request.method == "POST":
        username = request.POST.get("username").strip()
        email = request.POST.get("email").lower().strip()
        password = request.POST.get("password").strip()
        remember = request.POST.get("rememberme")

        if not remember:
            messages.error(request, "Iltimos, foydalanish shartlariga rozilik bildiring!")
            return redirect("sign-up")

        if not username or not email or not password:
            messages.error(request, "Iltimos, barcha maydonlarni to'ldiring!")
            return redirect("sign-up")
        
        if not utils.is_strong_password(password):
            messages.error(request, "Kechirasiz, parol yetarli darajada kuchli emas!")
            return redirect("sign-up")
        
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Kechirasiz, bu taxallus allaqachon mavjud!")
            return redirect("sign-up")
        
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Kechirasiz, bu email allaqachon mavjud!")
            return redirect("sign-up")
        
        user = CustomUser.objects.create_user(username=username, email=email, password=password)
        
        login(request, user)
        messages.success(request, "Tizimga muvaffaqiyatli kirdingiz!")
        
        return redirect("index") 
    
    context = {
        **get_base_context(request),
        'title': 'Ro\'yxatdan o\'tish',
    }

    return render(request, 'accounts/sign-up.html', context)

def sign_out(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "Tizimdan muvaffaqiyatli chiqdingiz.")
    
    return redirect("index")