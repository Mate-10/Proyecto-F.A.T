"""
URL configuration for Emergencia project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
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
    path('admin/', admin.site.urls),
]
