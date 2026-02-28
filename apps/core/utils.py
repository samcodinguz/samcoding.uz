from datetime import datetime
from django.core.paginator import Paginator

def get_base_context(request):

    return {
        'current_year': datetime.now().year
    }

def get_pagination_range(current_page, total_pages, delta=1):

    range_with_dots = []
    left = current_page - delta
    right = current_page + delta + 1
    range_with_dots.append(1)

    if left > 2:
        range_with_dots.append('...')

    for i in range(max(left, 2), min(right, total_pages)):
        range_with_dots.append(i)

    if right < total_pages:
        range_with_dots.append('...')

    if total_pages > 1:
        range_with_dots.append(total_pages)

    return range_with_dots

def paginate_queryset(queryset, request, per_page=5):

    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    pagination_range = get_pagination_range(page_obj.number, paginator.num_pages)
    return page_obj, pagination_range