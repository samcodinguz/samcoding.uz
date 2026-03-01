import hashlib
from apps.accounts import utils
from django.db.models import Q
from django.contrib import messages
from django.http import JsonResponse
from apps.core.utils import get_base_context, paginate_queryset
from django.shortcuts import render, redirect, get_object_or_404
from apps.accounts.models import CustomUser, PasswordResetToken
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from apps.locations.models import Region, District

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

def users(request):

    search = request.GET.get('search', '').strip()

    users = CustomUser.objects.all()
    if search:
        users = users.filter(Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(username__icontains=search))

    users, page_range = paginate_queryset(users, request, per_page=25)
    online_users = utils.get_top_active_users(limit=50)

    breadcrumb = [
        {"title": "home", "url": "index", 'args': []},
        {"title": "users", "url": "users", 'args': []}
    ]

    context = {
        **get_base_context(request),
        'title': "Foydalanuvchilar",
        'users': users,
        'page_range': page_range,
        'online_users': online_users,
        'breadcrumb': breadcrumb,
        'search': search
    }

    return render(request, "accounts/users/users.html", context)

def profile(request, username):
    user = get_object_or_404(CustomUser, username=username)

    breadcrumb = [
        {"title": "home", "url": "index", 'args': []},
        {"title": "users", "url": "users", 'args': []},
        {"title": f"{user.first_name} {user.last_name}", "url": "profile", 'args': [user.username]},
    ]

    context = {
        **get_base_context(request),
        'title': "Profil",
        'user': user,
        'breadcrumb': breadcrumb,
        'days': utils.contribution(),
        'year': 2026,
    }

    return render(request, "accounts/profile/profile.html", context)

def profile_settings(request, username):
    user = get_object_or_404(CustomUser, username=username)
    
    if request.user != user:
        return redirect("profile", username=username)
    
    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        region = request.POST.get("region")
        district = request.POST.get("district")
        school = request.POST.get("school", "").strip()
        shirt_size = request.POST.get("shirt_size")
        phone = request.POST.get("phone", "").strip()
        email = request.POST.get("email", "").lower().strip()

        if not all([first_name, last_name, region, district, school, phone, email]):
            messages.error(request, "Iltimos, barcha majburiy maydonlarni to'ldiring!")
            return redirect('profile-settings', username=username)
        
        user.first_name = first_name
        user.last_name = last_name

        region = get_object_or_404(Region, id=region)
        district = get_object_or_404(District, id=district, region=region)

        user.region = region
        user.district = district
        user.school = school
        
        if shirt_size:
            user.shirt_size = shirt_size
        
        user.phone = phone

        if CustomUser.objects.exclude(id=user.id).filter(email=email).exists():
            messages.error(request, "Bu email allaqachon mavjud!")
            return redirect('profile-settings', username=username)
        
        user.email = email
        
        tg_link = request.POST.get("tg_link", "").strip()
        gh_link = request.POST.get("gh_link", "").strip()
        cf_link = request.POST.get("cf_link", "").strip()
        fb_link = request.POST.get("fb_link", "").strip()

        if tg_link:
            user.tg_link = tg_link
        
        if gh_link:
            user.gh_link = gh_link

        if cf_link:
            user.cf_link = cf_link

        if fb_link:
            user.fb_link = fb_link     
        
        old_password = request.POST.get("old_password","").strip()
        new_password1 = request.POST.get("new_password1", "").strip()
        new_password2 = request.POST.get("new_password2", "").strip()

        if not user.has_usable_password():

            if not all([new_password1, new_password2]):
                messages.error(request, "Parol kiritish majburiy!")
                return redirect('profile-settings',username=username)

            if new_password1 != new_password2:
                messages.error(request,"Parollar mos emas!")
                return redirect('profile-settings',username=username)
            
            if not utils.is_strong_password(new_password1):
                messages.error(request,"Parol yetarli darajada kuchli emas!")
                return redirect('profile-settings',username=username)

            user.set_password(new_password1)
        else:

            if new_password1 or new_password2:

                if new_password1 != new_password2:
                    messages.error(request,"Yangi parollar mos emas!")
                    return redirect('profile-settings',username=username)

                if not user.check_password(old_password):
                    messages.error(request,"Eski parol noto'g'ri!")
                    return redirect('profile-settings',username=username)

                if not utils.is_strong_password(new_password1):
                    messages.error(request,"Yangi parol yetarli darajada kuchli emas!")
                    return redirect('profile-settings',username=username)
                
                user.set_password(new_password1)
                update_session_auth_hash(request, user)
        
        avatar = request.FILES.get("avatar")
        if avatar:
            if user.avatar:
                user.avatar.delete(save=False)

            new_filename, processed_avatar = utils.square_avatar(avatar)
            user.avatar.save(new_filename, processed_avatar, save=False)

        user.save()
        messages.success(request, "Profilingiz muvaffaqiyatli yangilandi!")
        return redirect('profile-settings', username=username)
    
    regions = Region.objects.all()

    breadcrumb = [
        {"title": "home", "url": "index", 'args': []},
        {"title": "users", "url": "profile", 'args': [user.username]},
        {"title": f"{user.first_name} {user.last_name}", "url": "profile-settings", 'args': [user.username]},
    ]

    context = {
        **get_base_context(request),
        'title': "Sozlamalar",
        'user': user,
        'breadcrumb': breadcrumb,
        'regions': regions
    }

    return render(request, "accounts/profile/profile-settings.html", context)

def districts(request,region_id):
    region = get_object_or_404(Region,id=region_id)
    districts = District.objects.filter(region=region).values("id","name")
    return JsonResponse(list(districts), safe=False)