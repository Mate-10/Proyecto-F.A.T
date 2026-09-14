from django.contrib import admin
from .models import Accidentes, Contactos, DetalleTuto, Hospitales, ModoEmergencia, TipoAccidente, Tutoriales, Usuario

admin.site.register(Accidentes)
admin.site.register(Contactos)
admin.site.register(DetalleTuto)
admin.site.register(ModoEmergencia)
admin.site.register(TipoAccidente)
admin.site.register(Tutoriales)
admin.site.register(Usuario)
admin.site.register(Hospitales)