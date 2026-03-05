from django.urls import path
from .views import public, judge, admin

urlpatterns = [
    # -------- PUBLIC --------
    # -------- JUDGE --------
    # -------- ADMIN --------
    path('dashboard/tags', admin.admin_tags, name='admin-tags'),
    path('dashboard/tags/add', admin.admin_tags_add, name='admin-tags-add'),
    path('dashboard/tags/edit/<int:id>', admin.admin_tags_edit, name='admin-tags-edit'),
]