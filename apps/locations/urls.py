from django.urls import path
from .views import public, judge, admin

urlpatterns = [
    # -------- PUBLIC --------
    # -------- JUDGE --------
    # -------- ADMIN --------
    path('dashboard/regions', admin.admin_regions, name='admin-regions'),
    path('dashboard/regions/add', admin.admin_regions_add, name='admin-regions-add'),
    path('dashboard/regions/edit/<int:id>', admin.admin_regions_edit, name='admin-regions-edit'),
    path('dashboard/districts', admin.admin_districts, name='admin-districts'),
    path('dashboard/districts/add', admin.admin_districts_add, name='admin-districts-add'),
    path('dashboard/districts/edit/<int:id>', admin.admin_districts_edit, name='admin-districts-edit'),
]