from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('properties.urls', namespace='properties')),
    path('locations/', include('locations.urls', namespace='locations')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('admin-dashboard/', include('admin_dashboard.urls')),


    # ✅ Allauth (Google login only)
    path('accounts/', include('allauth.urls')),
]



# For serving media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
