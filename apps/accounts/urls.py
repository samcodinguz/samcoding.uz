from django.urls import path
from .views import public, judge, admin

urlpatterns = [
    # -------- PUBLIC --------
    path('sign-in', public.sign_in, name='sign-in'),
    path('sign-up', public.sign_up, name='sign-up'),
    path('sign-out', public.sign_out, name='sign-out'),
    path('reset-password', public.reset_password, name='reset-password'),
    path('reset-confirm/<str:token>', public.reset_confirm, name='reset-confirm'),
    path('users', public.users, name='users'),
    path('profile/<str:username>', public.profile, name='profile'),
    path('profile/<str:username>/settings', public.profile_settings, name='profile-settings'),
    path('api/regions/<int:region_id>/districts', public.districts),
    # -------- JUDGE --------
    # -------- ADMIN --------
    path('dashboard/users', admin.admin_users, name='admin-users'),
    path('dashboard/users/add', admin.admin_user_add, name='admin-user-add'),
    path('dashboard/users/<str:username>/settings', admin.admin_profile_settings, name='admin-profile-settings'),
    path("dashboard/users/toggle-judge", admin.toggle_judge, name="admin-toggle-judge"),
]