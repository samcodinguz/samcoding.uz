from django.shortcuts import render
from apps.core.utils import get_base_context

def index(request):

    context = {
        **get_base_context(request),
        'title': 'Bosh sahifa',
    }

    return render(request, "core/index.html", context)