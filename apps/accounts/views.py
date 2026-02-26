import hashlib
from . import utils
from django.contrib import messages
from apps.core.utils import get_base_context
from django.shortcuts import render, redirect, get_object_or_404
from .models import CustomUser, PasswordResetToken
from django.contrib.auth import authenticate, login, logout

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
        username = request.POST.get("username").lower().strip()
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


def reset_password(request):
    if request.user.is_authenticated:
        return redirect("index")
    
    if request.method == "POST":
        email = request.POST.get("email").lower().strip()

        if email:
            user = CustomUser.objects.filter(email=email).first()
            if user:
                utils.send_password_reset_email(user)
        
        messages.success(request, "Agar email mavjud bo'lsa, parolni tiklash ko'rsatmalari yuborildi. Pochtangizni tekshiring!")
        return redirect("sign-in")    

    context = {
        **get_base_context(request),
        'title': 'Parolni tiklash',
    }

    return render(request, 'accounts/reset-password.html', context)


def reset_confirm(request, token):
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    reset_obj = PasswordResetToken.objects.filter(token=token_hash).first()
    
    if not reset_obj:
        messages.error(request, "Havola yaroqsiz!")
        return redirect("sign-in")

    if reset_obj.is_expired():
        reset_obj.delete()
        messages.error(request, "Havola muddati tugagan!")
        return redirect("sign-in")

    
    if request.method == "POST":
        password = request.POST.get("password")

        if not password:
            messages.error(request, "Parolni kiriting!")
            return redirect(request.path)
        
        if not utils.is_strong_password(password):
            messages.error(request, "Kechirasiz, parol yetarli darajada kuchli emas!")
            return redirect(request.path)

        user = reset_obj.user
        user.set_password(password)
        user.save()

        reset_obj.delete()

        messages.success(request, "Parolingiz muvaffaqiyatli yangilandi!")
        return redirect("sign-in")

    context = {
        **get_base_context(request),
        'title': 'Yangi parolni o\'rnatish',
    }
    
    return render(request, "accounts/reset-confirm.html", context)

def profile(request, username):
    user = get_object_or_404(CustomUser, username=username)

    breadcrumb = [
        {"title": "home", "url": "index", 'args': []},
        {"title": "users", "url": "profile", 'args': [user.username]},
        {"title": f"@{user.username}", "url": "profile", 'args': [user.username]},
    ]

    context = {
        **get_base_context(request),
        'title': "Profil ma'lumotlari",
        'user': user,
        'breadcrumb': breadcrumb,
        'days': utils.contribution(request),
        'year': 2026,
    }

    return render(request, "accounts/profile/profile.html", context)