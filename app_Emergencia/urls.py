from django.contrib import admin
from django.urls import path
from app_Emergencia import views

urlpatterns = [
    path('', views.login, name='login'),
    path('login/', views.login, name='login'),
    path('registro/', views.registro, name='registro'),
    path('inicio/', views.inicio, name='inicio'),
    path('guia-emergencia/', views.guia_emergencia, name='guia_emergencia'),
    path('hospitales-cercanos/', views.hospitales_cercanos, name='hospitales_cercanos'),
    path('formulario-emergencia/', views.formulario_emergencia, name='formulario_emergencia'),
    path('tutoriales/', views.tutoriales, name='tutoriales'),
    path('admin/', admin.site.urls),
]