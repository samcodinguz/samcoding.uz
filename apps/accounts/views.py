from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from apps.core.utils import get_base_context

def sign_in(request):
    if request.user.is_authenticated:
        return redirect("index")
    
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        remember = request.POST.get("rememberme")

        if not username or not password:
            messages.error(request, "Iltimos, taxallus va parolni kiriting.")
            return redirect("sign-in")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            if not remember:
                request.session.set_expiry(0)
            messages.success(request, "Tizimga muvaffaqiyatli kirdingiz.")
            return redirect("index")
        
        messages.error(request, "Taxallus yoki parol noto'g'ri.")
        return redirect("sign-in")

    context = {
        **get_base_context(request),
        'title': 'Kirish',
    }

    return render(request, 'accounts/sign-in.html', context)


def sign_out(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "Tizimdan muvaffaqiyatli chiqdingiz.")
    
    return redirect("index")