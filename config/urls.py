from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from . import errors

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('', include('apps.accounts.urls')),
    path('', include('apps.contests.urls')),
    path('', include('apps.locations.urls')),
    path('', include('apps.problems.urls')),
    path('', include('apps.ratings.urls')),
    path('', include('apps.submissions.urls')),
    path('accounts/', include('allauth.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler400 = errors.error_400
handler401 = errors.error_401
handler402 = errors.error_402
handler403 = errors.error_403
handler404 = errors.error_404
handler408 = errors.error_408
handler500 = errors.error_500