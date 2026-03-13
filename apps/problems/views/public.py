from django.db.models import Q
from django.contrib import messages
from apps.core.utils import get_base_context, paginate_queryset, apply_sorting
from django.shortcuts import render, redirect, get_object_or_404
from apps.problems.models import Problem, Language
from apps.submissions.models import Submission
from apps.problems.utils import validate_statement, parse_statement

def problems(request):

    search = request.GET.get('search', '').strip()
    sort = request.GET.get("sort")
    direction = request.GET.get("direction")

    allowed_sorts = {
        "id": "id",
        "difficulty": "difficulty",
        "accepted_count": "accepted_count",
    }

    problems = Problem.objects.filter(is_verified=True)
    problems = apply_sorting(problems, request, allowed_sorts, default="-id")
    if search:
        problems = problems.filter(Q(title__icontains=search))

    problems, page_range = paginate_queryset(problems, request, per_page=25)

    breadcrumb = [
        {"title": "home", "url": "index", 'args': []},
        {"title": "problems", "url": "problems", 'args': []}
    ]

    context = {
        **get_base_context(request),
        'title': "Masalalar",
        'problems': problems,
        'page_range': page_range,
        'breadcrumb': breadcrumb,
        'search': search,
        'sort': sort,
        'direction': direction,
    }

    return render(request, "problems/public/problems.html", context)

def problem(request, id):

    problem = get_object_or_404(Problem, id=id)
    sections = parse_statement(problem.statement, problem)
    languages = Language.objects.all().order_by('order')

    if request.method == "POST":
        
        code = request.POST.get("code")
        language = request.POST.get("language")

        if not all([code, language]):
            messages.error(request, "Yechim yuborilmadi!")
            return redirect("problem", id=id)
        
        if not request.user.is_authenticated:
            messages.error(request, "Yechim yuborish uchun tizimga kiring!")
            return redirect("sign-in")
        
        Submission.objects.create(
            user=request.user,
            problem=problem,
            language_id=language,
            code=code,
        )
        return redirect('problem', id=id)

    breadcrumb = [
        {"title": "home", "url": "index", 'args': []},
        {"title": "problems", "url": "problems", 'args': []},
        {"title": f"{id:04d}", "url": "problem", 'args': [id]}
    ]
    
    context = {
        **get_base_context(request),
        "title": f"Masala #{id:04d}",
        "breadcrumb": breadcrumb,
        "problem": problem,
        "languages": languages,
        "last_language": languages.first(),
        "sections": sections,
    }

    return render(request, "problems/public/problem.html", context)