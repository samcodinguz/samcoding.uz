from datetime import datetime
from django.db.models import F
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

def apply_sorting(queryset, request, allowed_sorts, nulls_last=None, default="id"):
    sort = request.GET.get("sort")
    direction = request.GET.get("direction")

    nulls_last = nulls_last or []

    field = allowed_sorts.get(sort, default)

    # NULL qiymatlar bo'lishi mumkin bo'lgan ustunlar
    if sort in nulls_last:
        if direction == "asc":
            return queryset.order_by(F(field).asc(nulls_last=True))
        return queryset.order_by(F(field).desc(nulls_last=True))

    if direction == "desc":
        field = f"-{field}"

    return queryset.order_by(field)