from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from app_Emergencia import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('registro/', views.registro, name='registro'),
    path('', views.login, name='entrada'),
    path('inicio/', views.inicio, name='inicio'),
    path('guia-de-emergencia/', views.guia_emergencia, name='guia_emergencia'),
    path('hospitales-cercanos/', views.hospitales_cercanos, name='hospitales_cercanos'),
    path('formulario-de-emergencia/', views.formulario_emergencia, name='formulario_emergencia'),
    path('tutoriales/', views.tutoriales, name='tutoriales'),
    path('sos/', views.sos, name='sos'),
    path('admin/', admin.site.urls),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
