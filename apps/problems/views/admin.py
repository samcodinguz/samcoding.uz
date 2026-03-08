import json
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from apps.core.utils import get_base_context, paginate_queryset, apply_sorting
from apps.problems.models import ProblemTag, Problem, ProblemImage, SampleTest
from django.contrib import messages
from apps.accounts.utils import uid_filename
from apps.problems.utils import validate_statement
from django.http import JsonResponse

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
        "author_username": "username",
        "created_at": "created_at",
        "is_verified": "verified",
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

    if request.method == "POST":

        title = request.POST.get("title")
        statement = request.POST.get("statement")

        if not all([title, statement]):
            messages.error(request, "Iltimos, barcha majburiy maydonlarni to'ldiring!")
            return redirect("admin-problems-add")
        
        if Problem.objects.filter(title=title).exists():
            messages.error(request, "Bu nomli masala allaqachon mavjud")
            return redirect("admin-problems-add")
        
        missing = validate_statement(statement)
        if missing:
            messages.error(request, f"{missing} bo'limi mavjud emas!")
            return redirect("admin-problems-add")
        
        problem = Problem.objects.create(
            title=title,
            statement=statement,
            author=request.user
        )

        inputs = request.POST.getlist("sample_input[]")
        outputs = request.POST.getlist("sample_output[]")

        for i, (inp, out) in enumerate(zip(inputs, outputs)):
            if inp and out:
                SampleTest.objects.create(
                    problem=problem,
                    input_data=inp,
                    output_data=out,
                    order=i
                )
        
        images = request.FILES.getlist("images[]")
        for img in images:
            if not img.content_type.startswith("image"):
                messages.error(request, "Faqat rasm yuklash mumkin")
                return redirect("admin-problems-add")
            
            if img.size > 1024 * 1024:
                messages.error(request, "Rasm 1MB dan katta bo'lmasligi kerak!")
                return redirect("admin-problems-add")

            ProblemImage.objects.create(
                problem=problem,
                image=img,
                original_name=img.name
            )

        messages.success(request, "Masala muvaffaqiyatli qo'shildi!")
        return redirect("admin-problems-edit", id=problem.id)
    
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

@login_required
def admin_problems_edit(request, id):
    if not request.user.is_superuser:
        raise PermissionDenied

    problem = get_object_or_404(Problem, id=id)

    if request.method == "POST":

        title = request.POST.get("title")
        statement = request.POST.get("statement")

        if not all([title, statement]):
            messages.error(request, "Iltimos, barcha majburiy maydonlarni to'ldiring!")
            return redirect("admin-problems-edit", id=problem.id)
        
        if Problem.objects.exclude(id=problem.id).filter(title=title).exists():
            messages.error(request, "Bu nomli masala allaqachon mavjud")
            return redirect("admin-problems-edit", id=problem.id)
        
        missing = validate_statement(statement)
        if missing:
            messages.error(request, f"{missing} bo'limi mavjud emas!")
            return redirect("admin-problems-edit", id=problem.id)
        
        problem.title = title
        problem.statement = statement
        problem.save()

        inputs = request.POST.getlist("sample_input[]")
        outputs = request.POST.getlist("sample_output[]")
        problem.samples.all().delete()

        for i, (inp, out) in enumerate(zip(inputs, outputs)):
            if inp and out:
                SampleTest.objects.create(
                    problem=problem,
                    input_data=inp,
                    output_data=out,
                    order=i
                )

        delete_images = request.POST.getlist("delete_images[]")
        delete_images = [i for i in delete_images if i]

        if delete_images:
            images = ProblemImage.objects.filter(id__in=delete_images, problem=problem)

            for img in images:
                if img.image:
                    img.image.delete(save=False)

            images.delete()

        images = request.FILES.getlist("images[]")
        for img in images:
            if not img.content_type.startswith("image"):
                messages.error(request, "Rasm formati noto'g'ri!")
                return redirect("admin-problems-edit", id=problem.id)
            
            if img.size > 1024 * 1024:
                messages.error(request, "Rasm hajmi 1MB dan oshmasligi kerak")
                return redirect("admin-problems-edit", id=problem.id)
            ProblemImage.objects.create(problem=problem, image=img, original_name=img.name)

        messages.success(request, "Masala muvaffaqiyatli yangilandi")
        return redirect("admin-problems-edit", id=problem.id)
    
    tags = ProblemTag.objects.all()

    breadcrumb = [
        {"title": "dashboard", "url": "admin-index", "args": []},
        {"title": "problems", "url": "admin-problems", "args": []},
        {"title": "edit", "url": "admin-problems-edit", "args": [id]},
    ]

    context = {
        **get_base_context(request),
        "title": "Masala tahrirlash",
        "problem": problem,
        "tags": tags,
        'breadcrumb': breadcrumb,
    }

    return render(request, "problems/admin/problem-edit.html", context)

@login_required
def admin_problems_test_edit(request, id):
    if not request.user.is_superuser:
        raise PermissionDenied

    problem = get_object_or_404(Problem, id=id)

    if request.method == 'POST':
        if request.POST.get("delete_test"):
            if problem.test_file:
                problem.test_file.delete(save=False)
                problem.test_file = None
                problem.sample_tests = 0
                problem.save()
                messages.success(request, "Test o'chirildi!")
                return redirect("admin-problems-test-edit", id=id)
        
        test_file = request.FILES.get("test_file")
        sample_tests = request.POST.get("sample_tests")

        if test_file:
            if not test_file.name.endswith(".zip"):
                messages.error(request, "Faqat *.zip fayl yuklash mumkin!")
                return redirect("admin-problems-test-edit", id=id)

            if problem.test_file:
                problem.test_file.delete(save=False)

            test_file.name = uid_filename(test_file.name)
            problem.test_file = test_file

        if not problem.test_file:
            messages.error(request, "Test yuklash majburiy!")
            return redirect("admin-problems-test-edit", id=id)

        if sample_tests:
            problem.sample_tests = sample_tests

        problem.save()

        messages.success(request, "Testlar saqlandi!")
        return redirect("admin-problems-test-edit", id=id)
    
    tags = ProblemTag.objects.all().order_by('id')

    breadcrumb = [
        {"title": "dashboard", "url": "admin-index", "args": []},
        {"title": "problems", "url": "admin-problems", "args": []},
        {"title": "test", "url": "admin-problems-test-edit", "args": [id]},
    ]

    context = {
        **get_base_context(request),
        "title": "TestCase",
        "problem": problem,
        "tags": tags,
        'breadcrumb': breadcrumb,
    }

    return render(request, "problems/admin/test-edit.html", context)

@login_required
def toggle_verified(request):
    if not request.user.is_superuser:
        return JsonResponse({"success": False}, status=403)

    if request.method == "POST":
        data = json.loads(request.body)
        problem_id = data.get("problem_id")

        problem = get_object_or_404(Problem, id=problem_id)

        problem.is_verified = not problem.is_verified
        problem.save()

        return JsonResponse({"success": True})

    return JsonResponse({"success": False})