from apps.accounts import utils
from django.db.models import Q
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

    search = request.GET.get('search', '').strip()
    role = request.GET.get('role','all')

    users = CustomUser.objects.all()
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
    }

    return render(request, "accounts/admin/users.html", context)