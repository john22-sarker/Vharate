from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

# ===============================
# NON-TRANSLATED URLS
# ===============================
urlpatterns = [
    # Language switcher
    path('i18n/', include('django.conf.urls.i18n')),

    # Allauth (Google login)
    path('accounts/', include('allauth.urls')),
]

# ===============================
# TRANSLATED URLS (EN / BN)
# ===============================
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),

    path('', include('properties.urls', namespace='properties')),
    path('locations/', include('locations.urls', namespace='locations')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('admin-dashboard/', include('admin_dashboard.urls')),
)

# ===============================
# MEDIA FILES (DEV ONLY)
# ===============================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
