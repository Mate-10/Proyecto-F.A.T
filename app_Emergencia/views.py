import hashlib
import math
import re
import unicodedata
from pathlib import Path

import requests
from staticmap import StaticMap, CircleMarker
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from .models import Usuario, Hospitales, Accidentes


# ---------- Login y registro ----------

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

        nombre = (request.POST.get('nombre') or '').strip()
        ubicacion = (request.POST.get('ubicacion') or '').strip()
        telefono = (request.POST.get('telefono') or '').strip()
        email = (request.POST.get('email') or '').strip()
        contrasena = request.POST.get('contrasena') or ''

        # Validaciones según el tamaño de las columnas de la base de datos
        error = None

        if not nombre or not email or not contrasena:
            error = 'Completá nombre, correo y contraseña.'
        elif len(nombre) > 15:
            error = 'El nombre puede tener hasta 15 caracteres.'
        elif len(ubicacion) > 50:
            error = 'La ubicación puede tener hasta 50 caracteres.'
        elif len(telefono) > 10:
            error = 'El teléfono puede tener hasta 10 caracteres (sin espacios ni código de país).'
        elif len(email) > 100:
            error = 'El correo puede tener hasta 100 caracteres.'
        elif len(contrasena) > 100:
            error = 'La contraseña puede tener hasta 100 caracteres.'

        if error:
            return render(request, 'registro.html', {'error': error})

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


# ---------- Inicio ----------

def inicio(request):
    if 'id_usuario' not in request.session:
        return redirect('login')

    return render(request, 'inicio.html')


def guia_emergencia(request):

    return render(request, 'guia_emergencia.html')


# ---------- Hospitales cercanos ----------

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


def calcular_distancia(lat1, lon1, lat2, lon2):

    radio_tierra = 6371

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return radio_tierra * c


def hospitales_cercanos(request):

    if request.method != 'POST':
        return render(request, 'hospitales_cercanos.html')

    direccion_original = (request.POST.get('direccion') or '').strip()

    if not direccion_original:
        return render(request, 'hospitales_cercanos.html', {
            'error': 'Escribí una dirección para buscar.'
        })

    direccion = direccion_original

    if 'córdoba' not in direccion.lower() and 'cordoba' not in direccion.lower():
        direccion = f'{direccion}, Córdoba, Argentina'

    # 1) Buscar las coordenadas de la dirección
    try:
        respuesta = requests.get(
            'https://nominatim.openstreetmap.org/search',
            params={
                'q': direccion,
                'format': 'json',
                'countrycodes': 'ar',
                'viewbox': '-64.35,-31.30,-64.05,-31.55',
                'bounded': 1
            },
            headers={'User-Agent': 'app-emergencia/1.0 (tu_email@ejemplo.com)'},
            timeout=10,
        )
        respuesta.raise_for_status()
        resultados = respuesta.json()

    except (requests.ConnectionError, requests.Timeout):
        return render(request, 'hospitales_cercanos.html', {
            'error': 'No pudimos conectarnos para buscar tu dirección. '
                     'Revisá tu conexión a internet e intentá de nuevo en unos segundos.',
            'direccion': direccion_original,
        })

    except (requests.RequestException, ValueError):
        return render(request, 'hospitales_cercanos.html', {
            'error': 'El servicio de direcciones no está disponible en este momento. '
                     'Probá de nuevo en un rato.',
            'direccion': direccion_original,
        })

    if not resultados:
        return render(request, 'hospitales_cercanos.html', {
            'error': 'No encontramos esa dirección. Probá con calle y número, por ejemplo: Av. Colón 500.',
            'direccion': direccion_original,
        })

    lat_usuario = float(resultados[0]['lat'])
    lon_usuario = float(resultados[0]['lon'])

    # 2) Calcular distancias a los hospitales
    lista_hospitales = []

    for hospital in Hospitales.objects.all():

        coordenadas = coordenadas_hospitales_normalizadas.get(
            normalizar(hospital.nombre)
        )

        if coordenadas is None:
            print('NO MATCHEA:', repr(hospital.nombre))
            continue

        lat_hospital, lon_hospital = coordenadas

        hospital.distancia = calcular_distancia(
            lat_usuario, lon_usuario,
            lat_hospital, lon_hospital
        )
        hospital.imagen = imagenes_hospitales.get(hospital.nombre, 'img/hospital-default.jpg')
        hospital.lat = lat_hospital
        hospital.lon = lon_hospital
        hospital.maps_query = f'{hospital.nombre} {hospital.ubicacion}, Córdoba, Argentina'
        lista_hospitales.append(hospital)

    if not lista_hospitales:
        return render(request, 'hospitales_cercanos.html', {
            'error': 'No pudimos cargar los hospitales en este momento.',
            'direccion': direccion_original,
        })

    lista_hospitales.sort(key=lambda h: h.distancia)

    # 3) Mapa: si falla, igual se muestra la lista
    mapa_url = None

    try:
        carpeta = Path(settings.MEDIA_ROOT)
        carpeta.mkdir(parents=True, exist_ok=True)

        clave = hashlib.md5(
            f'{lat_usuario:.4f},{lon_usuario:.4f}'.encode()
        ).hexdigest()[:12]
        nombre_archivo = f'mapa_{clave}.png'
        ruta_imagen = carpeta / nombre_archivo

        if not ruta_imagen.exists():
            mapa = StaticMap(
                600, 400,
                url_template='https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                headers={'User-Agent': 'app-emergencia/1.0 (tu_email@ejemplo.com)'},
                tile_request_timeout=10,
            )
            mapa.add_marker(CircleMarker((lon_usuario, lat_usuario), 'red', 12))

            for hospital in lista_hospitales:
                mapa.add_marker(CircleMarker((hospital.lon, hospital.lat), 'blue', 12))

            mapa.render().save(ruta_imagen)

        mapa_url = settings.MEDIA_URL + nombre_archivo

    except Exception as e:
        print('Error al generar el mapa:', e)

    return render(request, 'hospitales_cercanos.html', {
        'mapa_url': mapa_url,
        'hospitales_cercanos': lista_hospitales,
        'direccion': direccion_original,
    })


# ---------- Formulario de emergencia -> Tutoriales ----------

REGLAS_EMERGENCIA = [
    ('rcp', r'paro cardi|\bno respira|\brcp\b|reanim|dejo de respirar'),
    ('infarto', r'infarto|dolor (de|en el) pecho|opresion en el pecho'),
    ('acv', r'\bacv\b|ataque cerebral|derrame cerebral|cara caida|habla arrastrada|no puede hablar'),
    ('bebe', r'bebe.*(atragant|ahog|asfix)|(atragant|ahog|asfix).*bebe'),
    ('atragantamiento', r'atragant|ahog|asfix|se trago'),
    ('alergia', r'alerg|anafilax|ronchas|labios hinchados|lengua hinchada|garganta cerrada'),
    ('electrico', r'electric|electrocut|descarga|corriente|cortocircuito|enchufe|\bcable'),
    ('quemadura', r'quem|escald|agua hirviendo|aceite hirviendo'),
    ('herida', r'herid|\bcort(e|ad[oa]|o|aron)\b|cortadura'),
    ('hemorragia', r'hemorrag|sangr'),
    ('fractura', r'fractur|hueso|quebr|esguince|luxac|dislocad|se rompio'),
    ('cabeza', r'golp\w*.*cabeza|cabeza.*golp|traumatismo|conmocion'),
    ('convulsion', r'convuls|epilep'),
    ('desmayo', r'desmay|desvanec|inconscien|conocimiento|\bmare'),
    ('picaduras', r'picadur|\bpic(o|aron)\b|mordedur|\bmordi|abeja|avispa|arana|alacran|escorpion|serpiente|vibora|culebra|\bperro'),
    ('intoxicacion', r'intoxic|envenen|veneno|toxic|ingiri|sobredosis|lavandina|monoxido|\bgas\b'),
    ('calor', r'golpe de calor|insolacion|calor|hipotermia|\bfrio|congel'),
]

CLAVES_TUTORIALES = {clave for clave, _ in REGLAS_EMERGENCIA}


def detectar_emergencia(descripcion):
    texto = normalizar(descripcion)

    for clave, patron in REGLAS_EMERGENCIA:
        if re.search(patron, texto):
            return clave

    return None


def formulario_emergencia(request):

    if request.method == 'POST':

        descripcion = request.POST.get('descripcion', '')
        clave = detectar_emergencia(descripcion)

        if clave:
            return redirect(f"{reverse('tutoriales')}?abrir={clave}#{clave}")

        return redirect(f"{reverse('tutoriales')}?no_encontrado=1")

    return render(request, 'formulario_emergencia.html')


def tutoriales(request):

    abrir = request.GET.get('abrir', '')

    if abrir not in CLAVES_TUTORIALES:
        abrir = ''

    return render(request, 'tutoriales.html', {
        'abrir': abrir,
        'no_encontrado': request.GET.get('no_encontrado') == '1',
    })


# ---------- SOS ----------

def sos(request):
    if 'id_usuario' not in request.session:
        return redirect('login')

    if request.method == 'POST':
        descripcion = request.POST.get('descripcion', '').strip()[:100]
        direccion = request.POST.get('direccion', '').strip()[:50]

        if not descripcion:
            return render(request, 'sos.html', {
                'error': 'Tenés que describir el peligro.',
                'direccion': direccion,
            })

        Accidentes.objects.create(
            id_usuario_id=request.session['id_usuario'],
            direccion=direccion or None,
            fecha_hora=timezone.now(),
            descripcion=descripcion,
        )
        messages.success(request, 'Alerta enviada. Mantené la calma, la ayuda está en camino.')
        return redirect('inicio')

    return render(request, 'sos.html')