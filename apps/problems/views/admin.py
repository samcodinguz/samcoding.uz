from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from apps.core.utils import get_base_context, paginate_queryset, apply_sorting
from apps.problems.models import ProblemTag, Problem
from django.contrib import messages

@login_required
def admin_tags(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    if request.method == "POST":
        single_id = request.POST.get("single_delete")
        ids = request.POST.getlist("ids")

        if single_id:
            tag = get_object_or_404(ProblemTag, id=single_id)
            tag.delete()
            messages.success(request, "Teg muvaffaqiyatli o'chirildi!")
        elif ids:
            tags = ProblemTag.objects.filter(id__in=ids)
            tags.delete()
            messages.success(request, "Teglar muvaffaqiyatli o'chirildi!")

        return redirect(request.get_full_path())
    
    search = request.GET.get("search", "").strip()
    
    sort = request.GET.get("sort")
    direction = request.GET.get("direction")

    allowed_sorts = {
        "id": "id",
        "name": "name",
    }

    tags = ProblemTag.objects.all()
    tags = apply_sorting(tags, request, allowed_sorts, default="id")

    if search:
        tags = tags.filter(Q(name__icontains=search))
    
    tags, page_range = paginate_queryset(tags, request, per_page=25)

    breadcrumb = [
        {"title": "dashboard", "url": "admin-index", "args": []},
        {"title": "tags", "url": "admin-tags", "args": []},
    ]

    context = {
        **get_base_context(request),
        'title': 'Teglar',
        'tags': tags,
        'page_range': page_range,
        'breadcrumb': breadcrumb,
        'search': search,
        'sort': sort,
        'direction': direction,
    }

    return render(request, "problems/admin/tags.html", context)

@login_required
def admin_tags_add(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    if request.method == "POST":
        tag_name = request.POST.get("tag_name", "").strip()

        if not tag_name:
            messages.error(request, "Teg nomini kiritish majburiy!")
            return redirect("admin-tags")

        if ProblemTag.objects.filter(name__iexact=tag_name).exists():
            messages.error(request, "Bu teg allaqachon mavjud!")
            return redirect("admin-tags")
        
        ProblemTag.objects.create(name=tag_name)

        messages.success(request, f"{tag_name} teg muvaffaqiyatli qo'shildi!")
        return redirect("admin-tags")
        
    return redirect("admin-tags")

@login_required
def admin_tags_edit(request, id):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    tag = get_object_or_404(ProblemTag, id=id)
    
    if request.method == "POST":
        tag_name = request.POST.get("tag_name", "").strip()
        
        if not tag_name:
            messages.error(request, "Teg nomini kiritish majburiy!")
            return redirect("admin-tags")

        if ProblemTag.objects.filter(name__iexact=tag_name).exclude(id=tag.id).exists():
            messages.error(request, "Bu teg allaqachon mavjud!")
            return redirect("admin-tags")
        
        tag.name = tag_name
        tag.save()
        
        messages.success(request, "Teg muvaffaqiyatli tahrirlandi!")
        return redirect("admin-tags")
    
    return redirect("admin-tags")

@login_required
def admin_problems(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    if request.method == "POST":

        single_id = request.POST.get("single_delete")
        ids = request.POST.getlist("ids")

        if single_id:
            problem = get_object_or_404(Problem, id=single_id)
            
            if not problem.is_verified:
                if problem.test_file:
                    problem.test_file.delete(save=False)

                problem.delete()
                messages.success(request, "Masala muvaffaqiyatli o'chirildi!")
            else:
                messages.error(request, "Tasdiqlangan masalani o'chirib bo'lmaydi!")
        
        elif ids:

            problems = Problem.objects.filter(id__in=ids, is_verified=False)

            if problems.exists():
                for problem in problems.only("test_file"):
                    if problem.test_file:
                        problem.test_file.delete(save=False)

                problems.delete()
                messages.success(request, "Masalalar muvaffaqiyatli o'chirildi!")
            else:
                messages.error(request, "Tasdiqlangan masalalarni o'chirib bo'lmaydi!")
        return redirect(request.get_full_path())
    
    search = request.GET.get("search", "").strip()
    
    sort = request.GET.get("sort")
    direction = request.GET.get("direction")

    allowed_sorts = {
        "id": "id",
        "title": "title",
    }

    problems = Problem.objects.select_related("author").prefetch_related("tags")
    problems = apply_sorting(problems, request, allowed_sorts, default="id")

    if search:
        problems = problems.filter(Q(title__icontains=search))
    
    problems, page_range = paginate_queryset(problems, request, per_page=25)

    breadcrumb = [
        {"title": "dashboard", "url": "admin-index", "args": []},
        {"title": "problems", "url": "admin-problems", "args": []},
    ]

    context = {
        **get_base_context(request),
        'title': 'Masalalar',
        'problems': problems,
        'page_range': page_range,
        'breadcrumb': breadcrumb,
        'search': search,
        'sort': sort,
        'direction': direction,
    }

    return render(request, "problems/admin/problems.html", context)

@login_required
def admin_problems_add(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    tags = ProblemTag.objects.all()

    breadcrumb = [
        {"title": "dashboard", "url": "admin-index", "args": []},
        {"title": "problems", "url": "admin-problems", "args": []},
        {"title": "add", "url": "admin-problems-add", "args": []},
    ]

    context = {
        **get_base_context(request),
        "title": "Masala qo'shish",
        "tags": tags,
        'breadcrumb': breadcrumb,
    }

    return render(request, "problems/admin/problem-add.html", context)