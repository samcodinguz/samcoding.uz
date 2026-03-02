import json
from django.db.models import Q
from apps.accounts import utils
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import render
from apps.core.utils import get_base_context
from apps.core.utils import get_base_context, paginate_queryset
from django.shortcuts import render, redirect, get_object_or_404
from apps.accounts.models import CustomUser
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
            
            deleted_count = users.count()
            for user in users:
                if user.avatar:
                    user.avatar.delete(save=False)

            users.delete()
            messages.success(request, f"{deleted_count} ta user muvaffaqiyatli o'chirildi!")
        
        return redirect(request.get_full_path())
    
    sort = request.GET.get("sort")
    direction = request.GET.get("direction")

    allowed_sorts = {
        "id": "id",
        "user": "username",
        "contact": "phone",
        "region": "region__name",
        "created": "date_joined",
        "status": "last_activity",
    }

    sort_field = allowed_sorts.get(sort, "id")

    if direction == "desc":
        sort_field = f"-{sort_field}"

    search = request.GET.get('search', '').strip()
    role = request.GET.get('role', 'all')

    users = CustomUser.objects.all().order_by(sort_field)
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