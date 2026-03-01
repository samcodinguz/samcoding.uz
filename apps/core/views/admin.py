from django.shortcuts import render
from apps.core.utils import get_base_context
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

@login_required
def admin_index(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    breadcrumb = [
        {"title": "dashboard", "url": "admin-index", 'args': []},
    ]

    context = {
        **get_base_context(request),
        'title': 'Bosh sahifa',
        'breadcrumb': breadcrumb,
    }

    return render(request, "core/admin/index.html", context)
    