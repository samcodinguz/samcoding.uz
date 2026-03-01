from django.urls import path
from .views import public, judge, admin

urlpatterns = [
    # -------- PUBLIC --------
    path('', public.index, name='index'),
    # -------- JUDGE --------
    # -------- ADMIN --------
    path('dashboard', admin.admin_index, name='admin-index'),
]