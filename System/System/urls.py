from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('Home.urls')),
    path('admin/', admin.site.urls),
    path('form/', include('Form.urls')),
    path('client/', include('Client.urls')),
    path('administrador/', include('administrador.urls')),
    path('doctor/', include('Doctor.urls')),
    path('recepcion/', include('recepcion.urls')),
    path("__reload__/", include("django_browser_reload.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
