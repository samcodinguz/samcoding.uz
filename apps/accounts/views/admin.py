import json
from django.db.models import Q
from apps.accounts import utils
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import render
from apps.core.utils import get_base_context, paginate_queryset, apply_sorting
from django.shortcuts import render, redirect, get_object_or_404
from apps.accounts.models import CustomUser, Region, District
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

# Create your views here.
@login_required
def admin_users(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    if request.method == "POST":

        single_id = request.POST.get("single_delete")
        ids = request.POST.getlist("ids")

        if single_id:
            user = get_object_or_404(CustomUser, id=single_id)

            if user.is_staff:
                messages.error(request, "Staff userni o'chirish mumkin emas!")
                return redirect(request.get_full_path())
            
            if user.avatar:
                user.avatar.delete(save=False)

            user.delete()
            messages.success(request, "User muvaffaqiyatli o'chirildi!")
        
        elif ids:

            users = CustomUser.objects.filter(id__in=ids).exclude(is_staff=True)

            if users.exists():
                for user in users.only("avatar"):
                    if user.avatar:
                        user.avatar.delete(save=False)

                users.delete()
                messages.success(request, "Userlar muvaffaqiyatli o'chirildi!")
            else:
                messages.error(request, "Staff userlarni o'chirib bo'lmaydi!")
        
        return redirect(request.get_full_path())

    role = request.GET.get('role', 'all')
    search = request.GET.get('search', '').strip()
    
    sort = request.GET.get("sort")
    direction = request.GET.get("direction")

    allowed_sorts = {
        "id": "id",
        "user": "username",
        "phone": "phone",
        "region": "region__name",
        "date_joined": "date_joined",
        "last_activity": "last_activity",
    }

    users = CustomUser.objects.select_related("region")
    users = apply_sorting(users, request, allowed_sorts, nulls_last=["last_activity", "phone", "region"], default="id")

    if search:
        users = users.filter(Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(username__icontains=search))

    if role == 'judge':
        users = users.filter(is_judge=True)
    elif role == 'nojudge':
        users = users.filter(is_judge=False)

    users, page_range = paginate_queryset(users, request, per_page=25)

    breadcrumb = [
        {"title": "dashboard", "url": "admin-index", 'args': []},
        {"title": "users", "url": "admin-users", 'args': []},
    ]

    context = {
        **get_base_context(request),
        'title': 'Foydalanuvchilar',
        'users': users,
        'page_range': page_range,
        'breadcrumb': breadcrumb,
        'search': search,
        'role': role,
        'sort': sort,
        'direction': direction,
    }

    return render(request, "accounts/admin/users.html", context)

@login_required
def admin_user_add(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    if request.method == 'POST':
        user_name = request.POST.get("user_name", "").strip()
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        password1 = request.POST.get("password1", "").strip()
        password2 = request.POST.get("password2", "").strip()

        email = request.POST.get("email", "").lower().strip()
        if email and CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Bu email allaqachon mavjud!")
            return redirect("admin-users")

        if not all([user_name, password1, password2]):
            messages.error(request, "Taxallus va parollar majburiy!")
            return redirect('admin-users')
        
        if password1 != password2:
            messages.error(request, "Parollar mos emas!")
            return redirect("admin-users")
        
        if CustomUser.objects.filter(username=user_name).exists():
            messages.error(request, "Bu taxallus allaqachon mavjud!")
            return redirect("admin-users")
        
        user = CustomUser.objects.create_user(
            username=user_name,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name,
        )

        messages.success(request, "Foydalanuvchi muvaffaqiyatli qo'shildi!")
        return redirect("admin-users")
    
    return redirect("admin-users")

@login_required
def admin_profile_settings(request, username):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    user = get_object_or_404(CustomUser, username=username)

    if request.method == "POST":
        user_name = request.POST.get("user_name", "").strip()
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        region = request.POST.get("region")
        district = request.POST.get("district")
        school = request.POST.get("school", "").strip()
        shirt_size = request.POST.get("shirt_size")
        phone = request.POST.get("phone", "").strip()
        email = request.POST.get("email", "").lower().strip()

        if user_name:
            if CustomUser.objects.exclude(id=user.id).filter(username=user_name).exists():
                messages.error(request, "Bu username allaqachon mavjud!")
                return redirect('admin-profile-settings', username=username)
            user.username = user_name
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if region and district:
            region = get_object_or_404(Region, id=region)
            district = get_object_or_404(District, id=district, region=region)
            user.region = region
            user.district = district
        if school:
            user.school = school
        if shirt_size:
            user.shirt_size = shirt_size
        if phone:
            user.phone = phone
        if email:
            if CustomUser.objects.exclude(id=user.id).filter(email=email).exists():
                messages.error(request, "Bu email allaqachon mavjud!")
                return redirect('admin-profile-settings', username=username)
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

        password1 = request.POST.get("password1", "").strip()
        password2 = request.POST.get("password2", "").strip()

        if all([password1, password2]):
            if password1 != password2:
                messages.error(request,"Parollar mos emas!")
                return redirect('admin-profile-settings', username=username)
        
            user.set_password(password1)
            if user == request.user:
                update_session_auth_hash(request, user)

        avatar = request.FILES.get("avatar")
        if avatar:
            if user.avatar:
                user.avatar.delete(save=False)

            new_filename, processed_avatar = utils.square_avatar(avatar)
            user.avatar.save(new_filename, processed_avatar, save=False)

        user.save()
        messages.success(request, f"@{user.username} ma'lumotlari muvaffaqiyatli yangilandi!")
        return redirect('admin-users')

    regions = Region.objects.all().order_by('id')

    breadcrumb = [
        {"title": "dashboard", "url": "admin-index", 'args': []},
        {"title": "users", "url": "admin-users", 'args': []},
        {"title": f"{user.first_name} {user.last_name}", "url": "admin-profile-settings", 'args': [user.username]},
    ]

    context = {
        **get_base_context(request),
        'title': 'Sozlamalar',
        'breadcrumb': breadcrumb,
        'user': user,
        'regions': regions
    }

    return render(request, "accounts/admin/settings.html", context)

@login_required
def toggle_judge(request):
    if not request.user.is_superuser:
        return JsonResponse({"success": False}, status=403)

    if request.method == "POST":
        data = json.loads(request.body)
        user_id = data.get("user_id")

        user = get_object_or_404(CustomUser, id=user_id)

        user.is_judge = not user.is_judge
        user.save()

        return JsonResponse({"success": True})

    return JsonResponse({"success": False})