from django.contrib import admin
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include('core.urls')),
    path("accounts/", include('django.contrib.auth.urls')), # django ya trae predefinadias rutas para autenticacion login y logout
]


if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
