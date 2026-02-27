from django.urls import path
from . import views

urlpatterns = [
    path('sign-in', views.sign_in, name='sign-in'),
    path('sign-up', views.sign_up, name='sign-up'),
    path('sign-out', views.sign_out, name='sign-out'),
    
    path('reset-password', views.reset_password, name='reset-password'),
    path('reset-confirm/<str:token>', views.reset_confirm, name='reset-confirm'),

    path('users', views.users, name='users'),
    path('profile/<str:username>', views.profile, name='profile'),
    path('profile/<str:username>/settings', views.profile_settings, name='profile-settings'),
    path('regions/<int:region_id>',views.districts, name='districts'),
]