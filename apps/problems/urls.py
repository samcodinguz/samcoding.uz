from django.urls import path
from .views import public, judge, admin

urlpatterns = [
    # -------- PUBLIC --------
    path('problems', public.problems, name='problems'),
    path('problems/<int:id>', public.problem, name='problem'),
    # -------- JUDGE --------
    # -------- ADMIN --------
    path('dashboard/problems', admin.admin_problems, name='admin-problems'),
    path('dashboard/problems/add', admin.admin_problems_add, name='admin-problems-add'),
    path('dashboard/problems/edit/<int:id>', admin.admin_problems_edit, name='admin-problems-edit'),
    path('dashboard/problems/test/add/<int:id>', admin.admin_problems_test_add, name='admin-problems-test-add'),
    path('dashboard/problems/tag/add/<int:id>', admin.admin_problems_tag_add, name='admin-problems-tag-add'),
    path('dashboard/problems/config/<int:id>', admin.admin_problems_config, name='admin-problems-config'),
    path('dashboard/tags', admin.admin_tags, name='admin-tags'),
    path('dashboard/tags/add', admin.admin_tags_add, name='admin-tags-add'),
    path('dashboard/tags/edit/<int:id>', admin.admin_tags_edit, name='admin-tags-edit'),
    path("dashboard/problems/toggle-verified", admin.toggle_verified, name="admin-toggle-verified"),
]