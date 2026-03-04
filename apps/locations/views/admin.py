from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from apps.core.utils import get_base_context, paginate_queryset, apply_sorting
from apps.locations.models import Region, District
from django.contrib import messages

@login_required
def admin_regions(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    if request.method == "POST":
        single_id = request.POST.get("single_delete")
        ids = request.POST.getlist("ids")

        if single_id:
            region = get_object_or_404(Region, id=single_id)
            region.delete()
            messages.success(request, "Viloyat muvaffaqiyatli o'chirildi!")
        elif ids:
            region = Region.objects.filter(id__in=ids)
            deleted_count = region.count()
            region.delete()
            messages.success(request, f"{deleted_count} ta viloyat muvaffaqiyatli o'chirildi!")

        return redirect(request.get_full_path())
    
    search = request.GET.get("search", "").strip()
    
    sort = request.GET.get("sort")
    direction = request.GET.get("direction")

    allowed_sorts = {
        "id": "id",
        "name": "name",
    }

    regions = Region.objects.all()
    regions = apply_sorting(regions, request, allowed_sorts, default="id")

    if search:
        regions = regions.filter(Q(name__icontains=search))
    
    regions, page_range = paginate_queryset(regions, request, per_page=25)

    breadcrumb = [
        {"title": "dashboard", "url": "admin-index", "args": []},
        {"title": "regions", "url": "admin-regions", "args": []},
    ]

    context = {
        **get_base_context(request),
        'title': 'Viloyatlar',
        'regions': regions,
        'page_range': page_range,
        'breadcrumb': breadcrumb,
        'search': search,
        'sort': sort,
        'direction': direction,
    }

    return render(request, "locations/admin/regions.html", context)

@login_required
def admin_regions_add(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    if request.method == "POST":
        name = request.POST.get("name", "").strip()

        if not name:
            messages.error(request, "Viloyat nomini kiritish majburiy!")
            return redirect("admin-regions")

        if Region.objects.filter(name__iexact=name).exists():
            messages.error(request, "Bu viloyat allaqachon mavjud!")
            return redirect("admin-regions")
        
        Region.objects.create(name=name)
        messages.success(request, f"{name} viloyati muvaffaqiyatli qo'shildi!")
        return redirect("admin-regions")
        
    return redirect("admin-regions")
    
@login_required
def admin_regions_edit(request, id):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    region = get_object_or_404(Region, id=id)
    
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        if not name:
            messages.error(request, "Viloyat nomini kiritish majburiy!")
            return redirect("admin-regions")

        if Region.objects.filter(name__iexact=name).exclude(id=region.id).exists():
            messages.error(request, "Bu viloyat allaqachon mavjud!")
            return redirect("admin-regions")
        
        region.name = name
        region.save()
        messages.success(request, "Viloyati nomi muvaffaqiyatli tahrirlandi!")
        return redirect("admin-regions")
    
    return redirect("admin-regions")

@login_required
def admin_districts(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    if request.method == "POST":
        single_id = request.POST.get("single_delete")
        ids = request.POST.getlist("ids")

        if single_id:
            district = get_object_or_404(District, id=single_id)
            district.delete()
            messages.success(request, "Tuman muvaffaqiyatli o'chirildi!")
        elif ids:
            district = District.objects.filter(id__in=ids)
            deleted_count = district.count()
            district.delete()
            messages.success(request, f"{deleted_count} ta tuman muvaffaqiyatli o'chirildi!")

        return redirect(request.get_full_path())
    
    search = request.GET.get("search", "").strip()
    
    sort = request.GET.get("sort")
    direction = request.GET.get("direction")

    allowed_sorts = {
        "id": "id",
        "name": "name",
    }

    districts = District.objects.all().select_related("region")
    districts = apply_sorting(districts, request, allowed_sorts, default="id")

    if search:
        districts = districts.filter(Q(name__icontains=search))
    
    districts, page_range = paginate_queryset(districts, request, per_page=25)
    regions = Region.objects.all().order_by('id')

    breadcrumb = [
        {"title": "dashboard", "url": "admin-index", "args": []},
        {"title": "districts", "url": "admin-districts", "args": []},
    ]

    context = {
        **get_base_context(request),
        'title': 'Tumanlar',
        'districts': districts,
        'regions': regions,
        'page_range': page_range,
        'breadcrumb': breadcrumb,
        'search': search,
        'sort': sort,
        'direction': direction,
    }

    return render(request, "locations/admin/districts.html", context)

@login_required
def admin_districts_add(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    if request.method == "POST":
        region_id = request.POST.get("region_id")
        district_name = request.POST.get("district_name", "").strip()

        if not region_id or not district_name:
            messages.error(request, "Viloyat va tuman nomini kiritish majburiy!")
            return redirect("admin-districts")

        if District.objects.filter(region_id=region_id, name__iexact=district_name).exists():
            messages.error(request, "Bu tuman allaqachon mavjud!")
            return redirect("admin-districts")
        
        District.objects.create(region_id=region_id, name=district_name)

        messages.success(request, f"{district_name} tuman muvaffaqiyatli qo'shildi!")
        return redirect("admin-districts")
        
    return redirect("admin-districts")

@login_required
def admin_districts_edit(request, id):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    district = get_object_or_404(District, id=id)
    
    if request.method == "POST":
        region_id = request.POST.get("region_id")
        district_name = request.POST.get("district_name", "").strip()
        
        if not region_id or not district_name:
            messages.error(request, "Viloyat va tuman nomini kiritish majburiy!")
            return redirect("admin-districts")

        if District.objects.filter(region_id=region_id, name__iexact=district_name).exclude(id=district.id).exists():
            messages.error(request, "Bu tuman allaqachon mavjud!")
            return redirect("admin-districts")
        
        district.region_id = region_id
        district.name = district_name
        district.save()
        
        messages.success(request, "Tuman muvaffaqiyatli tahrirlandi!")
        return redirect("admin-districts")
    
    return redirect("admin-districts")