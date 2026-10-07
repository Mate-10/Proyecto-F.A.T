import math
import unicodedata
import requests
from staticmap import StaticMap, CircleMarker
from django.conf import settings
from django.shortcuts import render, redirect
from .models import Usuario, Hospitales


def login(request):

    if request.method == 'POST':

        email = request.POST.get('email')
        contrasena = request.POST.get('contrasena')

        usuario = Usuario.objects.filter(
            email=email,
            contrasena=contrasena
        ).first()

        if usuario:

            request.session['id_usuario'] = usuario.id_usuario

            return redirect('inicio')

        else:

            return render(request, 'login.html', {
                'error': 'Correo o contraseña incorrectos.'
            })

    return render(request, 'login.html')


def registro(request):

    if request.method == 'POST':

        nombre = request.POST.get('nombre')
        ubicacion = request.POST.get('ubicacion')
        telefono = request.POST.get('telefono')
        email = request.POST.get('email')
        contrasena = request.POST.get('contrasena')

        usuario_existente = Usuario.objects.filter(
            email=email
        ).first()

        if usuario_existente:

            return render(request, 'registro.html', {
                'error': 'Este correo ya está registrado.'
            })

        Usuario.objects.create(
            nombre=nombre,
            ubicacion=ubicacion,
            telefono=telefono,
            email=email,
            contrasena=contrasena
        )

        return redirect('login')

    return render(request, 'registro.html')


def inicio(request):
    if 'id_usuario' not in request.session:
        return redirect('login')

    return render(request, 'inicio.html')


def guia_emergencia(request):

    return render(request, 'guia_emergencia.html')


imagenes_hospitales = {
    'Hospital Nacional de Clínicas': 'img/hospitalclinicascordoba.webp',
    'Hospital San Roque': 'img/hopital_sanroque.webp',
    'Hospital de Urgencias (H.M.U.)': 'img/Hospital de Urgencias (H.M.U.).jpg',
    'Hospital de Niños de la Santísima Trinidad': 'img/hospital_de_niños_de_la_santisima_trinidad.webp',
    'Hospital Pediátrico del Niño Jesús': 'img/hospital-pediatrico-ninio-jesus.webp',
    'Hospital Italiano de Córdoba': 'img/hospital-italiano-cordoba-2059131.webp',
    'Hospital Córdoba': 'img/hospital-cordoba.webp',
    'Sanatorio Allende (Nueva Córdoba)': 'img/sanatorio_allende-nueva_cordoba.jpg',
}

coordenadas_hospitales = {
    'Hospital Nacional de Clínicas': (-31.406402, -64.203261),
    'Hospital San Roque': (-31.417547, -64.179087),
    'Hospital de Urgencias (H.M.U.)': (-31.412831, -64.175937),
    'Hospital de Niños de la Santísima Trinidad': (-31.427542, -64.169082),
    'Hospital Pediátrico del Niño Jesús': (-31.399155, -64.197519),
    'Hospital Italiano de Córdoba': (-31.409382, -64.164624),
    'Hospital Córdoba': (-31.406446, -64.158075),
    'Sanatorio Allende (Nueva Córdoba)': (-31.424782, -64.187395),
}


def normalizar(texto):
    texto = texto.strip().lower()
    texto = unicodedata.normalize('NFKD', texto)
    texto = ''.join(c for c in texto if not unicodedata.combining(c))
    return texto


coordenadas_hospitales_normalizadas = {
    normalizar(nombre): coords
    for nombre, coords in coordenadas_hospitales.items()
}


def hospitales_cercanos(request):

    if request.method == 'POST':

        direccion = request.POST.get('direccion')

        if 'córdoba' not in direccion.lower() and 'cordoba' not in direccion.lower():
            direccion = f'{direccion}, Córdoba, Argentina'

        respuesta = requests.get(
            'https://nominatim.openstreetmap.org/search',
            params={
                'q': direccion,
                'format': 'json',
                'countrycodes': 'ar',
                'viewbox': '-64.35,-31.30,-64.05,-31.55',
                'bounded': 1
            },
            headers={'User-Agent': 'app-emergencia'}
        )

        resultados = respuesta.json()

        if not resultados:
            return render(request, 'hospitales_cercanos.html', {
                'error': 'No se encontró esa dirección.'
            })

        lat_usuario = float(resultados[0]['lat'])
        lon_usuario = float(resultados[0]['lon'])

        hospitales = Hospitales.objects.all()
        lista_hospitales = []

        for hospital in hospitales:

            coordenadas = coordenadas_hospitales_normalizadas.get(
                normalizar(hospital.nombre)
            )

            if coordenadas is None:
                print('NO MATCHEA:', repr(hospital.nombre))
                continue

            lat_hospital, lon_hospital = coordenadas

            distancia = calcular_distancia(
                lat_usuario, lon_usuario,
                lat_hospital, lon_hospital
            )

            hospital.distancia = distancia
            hospital.imagen = imagenes_hospitales.get(hospital.nombre, 'img/hospital-default.jpg')
            hospital.lat = lat_hospital
            hospital.lon = lon_hospital
            hospital.maps_query = f'{hospital.nombre} {hospital.ubicacion}, Córdoba, Argentina'
            lista_hospitales.append(hospital)

        lista_hospitales.sort(key=lambda h: h.distancia)

        mapa = StaticMap(600, 400)
        mapa.add_marker(CircleMarker((lon_usuario, lat_usuario), 'red', 12))

        for hospital in lista_hospitales:
            mapa.add_marker(CircleMarker((hospital.lon, hospital.lat), 'blue', 12))

        imagen = mapa.render()
        ruta_imagen = settings.MEDIA_ROOT / 'mapa_temp.png'
        imagen.save(ruta_imagen)

        return render(request, 'hospitales_cercanos.html', {
            'mapa_url': settings.MEDIA_URL + 'mapa_temp.png',
            'hospitales_cercanos': lista_hospitales
        })

    return render(request, 'hospitales_cercanos.html')


def calcular_distancia(lat1, lon1, lat2, lon2):

    radio_tierra = 6371

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return radio_tierra * c
def formulario_emergencia(request):

    return render(request, 'formulario_emergencia.html')


def tutoriales(request):

    return render(request, 'tutoriales.html')