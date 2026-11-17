# ============================================================
# IMPORTACIONES
# ============================================================
import hashlib          # Para generar un "hash" (código único) que sirve de nombre de archivo del mapa
import math             # Funciones matemáticas (seno, coseno, raíz...) para calcular distancias
import re               # Expresiones regulares: buscar patrones de texto (usado para detectar emergencias)
import unicodedata      # Para quitar tildes de los textos (normalizar)
from pathlib import Path  # Manejo cómodo de rutas de carpetas y archivos

import requests         # Para hacer peticiones HTTP a servicios externos (Nominatim)
from staticmap import StaticMap, CircleMarker  # Para generar la imagen del mapa con puntos de colores
from django.conf import settings                # Acceso a la configuración del proyecto (settings.py)
from django.contrib import messages             # Mensajes temporales para el usuario (ej: "Alerta enviada")
from django.shortcuts import render, redirect   # render: muestra un HTML / redirect: manda a otra URL
from django.urls import reverse                 # Convierte el nombre de una URL en su ruta real
from django.utils import timezone               # Fecha y hora actual (con zona horaria)
from .models import Usuario, Hospitales, Accidentes  # Modelos (tablas de la base de datos)


# ============================================================
# LOGIN Y REGISTRO
# ============================================================

def login(request):
    # Vista del inicio de sesión

    # Si el formulario fue enviado (método POST)
    if request.method == 'POST':

        # Se leen los datos que escribió el usuario en el formulario
        email = request.POST.get('email')
        contrasena = request.POST.get('contrasena')

        # Se busca en la base de datos un usuario que coincida con email y contraseña
        # .first() devuelve el primero encontrado, o None si no hay ninguno
        usuario = Usuario.objects.filter(
            email=email,
            contrasena=contrasena
        ).first()

        # Si se encontró el usuario, las credenciales son correctas
        if usuario:

            # Se guarda el id en la sesión: así el sistema "recuerda" que está logueado
            request.session['id_usuario'] = usuario.id_usuario

            # Se lo manda a la página de inicio
            return redirect('inicio')

        else:

            # Si no existe, se vuelve a mostrar el login con un mensaje de error
            return render(request, 'login.html', {
                'error': 'Correo o contraseña incorrectos.'
            })

    # Si es GET (entra por primera vez a la página), solo se muestra el formulario vacío
    return render(request, 'login.html')


def registro(request):
    # Vista para crear una cuenta nueva

    if request.method == 'POST':

        # Se leen los datos del formulario. "or ''" evita errores si el campo viene vacío (None)
        # .strip() elimina espacios al principio y al final
        nombre = (request.POST.get('nombre') or '').strip()
        ubicacion = (request.POST.get('ubicacion') or '').strip()
        telefono = (request.POST.get('telefono') or '').strip()
        email = (request.POST.get('email') or '').strip()
        contrasena = request.POST.get('contrasena') or ''

        # Validaciones según el tamaño de las columnas de la base de datos
        # Si algo falla, se guarda el mensaje en la variable "error"
        error = None

        if not nombre or not email or not contrasena:
            # Estos tres campos son obligatorios
            error = 'Completá nombre, correo y contraseña.'
        elif len(nombre) > 15:
            # len() cuenta los caracteres; la columna nombre admite máximo 15
            error = 'El nombre puede tener hasta 15 caracteres.'
        elif len(ubicacion) > 50:
            error = 'La ubicación puede tener hasta 50 caracteres.'
        elif len(telefono) > 10:
            error = 'El teléfono puede tener hasta 10 caracteres (sin espacios ni código de país).'
        elif len(email) > 100:
            error = 'El correo puede tener hasta 100 caracteres.'
        elif len(contrasena) > 100:
            error = 'La contraseña puede tener hasta 100 caracteres.'

        # Si hubo algún error, se vuelve al formulario mostrando el mensaje
        if error:
            return render(request, 'registro.html', {'error': error})

        # Se verifica que no exista ya un usuario con ese correo
        usuario_existente = Usuario.objects.filter(
            email=email
        ).first()

        if usuario_existente:

            return render(request, 'registro.html', {
                'error': 'Este correo ya está registrado.'
            })

        # Si todo está bien, se crea el usuario nuevo (INSERT en la base de datos)
        Usuario.objects.create(
            nombre=nombre,
            ubicacion=ubicacion,
            telefono=telefono,
            email=email,
            contrasena=contrasena
        )

        # Después de registrarse, se lo manda al login
        return redirect('login')

    # Si es GET, se muestra el formulario de registro vacío
    return render(request, 'registro.html')


# ============================================================
# INICIO
# ============================================================

def inicio(request):
    # Página principal (solo para usuarios logueados)

    # Si en la sesión no está guardado el id_usuario, no inició sesión: se lo manda al login
    if 'id_usuario' not in request.session:
        return redirect('login')

    return render(request, 'inicio.html')


def guia_emergencia(request):
    # Muestra una página informativa fija (no requiere login)

    return render(request, 'guia_emergencia.html')


# ============================================================
# HOSPITALES CERCANOS
# ============================================================

# Diccionario: nombre del hospital -> ruta de su imagen (dentro de la carpeta static)
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

# Diccionario: nombre del hospital -> (latitud, longitud)
# Sirve para calcular la distancia sin consultar un servicio externo
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
    # Deja el texto "limpio" para poder compararlo: sin espacios extra, en minúsculas y sin tildes
    # Ejemplo: "  Córdoba " -> "cordoba"
    texto = texto.strip().lower()
    # NFKD separa cada letra de su tilde (ej: "é" -> "e" + "´")
    texto = unicodedata.normalize('NFKD', texto)
    # Se descartan los caracteres que son tildes (combining) y se vuelve a unir el texto
    texto = ''.join(c for c in texto if not unicodedata.combining(c))
    return texto


# Mismo diccionario de coordenadas, pero con los nombres normalizados
# Así "Hospital Nacional de Clínicas" de la BD coincide aunque tenga distintas tildes o mayúsculas
coordenadas_hospitales_normalizadas = {
    normalizar(nombre): coords
    for nombre, coords in coordenadas_hospitales.items()
}


def calcular_distancia(lat1, lon1, lat2, lon2):
    # Calcula la distancia en km entre dos puntos del planeta con la fórmula de Haversine
    # (tiene en cuenta que la Tierra es una esfera)

    radio_tierra = 6371  # Radio de la Tierra en kilómetros

    # Las funciones trigonométricas trabajan en radianes, por eso se convierten los grados
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)   # Diferencia de latitud
    delta_lon = math.radians(lon2 - lon1)   # Diferencia de longitud

    # Fórmula de Haversine
    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Distancia final = radio * ángulo
    return radio_tierra * c


def hospitales_cercanos(request):
    # Recibe una dirección, la convierte en coordenadas y muestra los hospitales ordenados por cercanía

    # Si entra por GET, solo se muestra el formulario
    if request.method != 'POST':
        return render(request, 'hospitales_cercanos.html')

    # Dirección que escribió el usuario (sin espacios sobrantes)
    direccion_original = (request.POST.get('direccion') or '').strip()

    # Si no escribió nada, se muestra un error
    if not direccion_original:
        return render(request, 'hospitales_cercanos.html', {
            'error': 'Escribí una dirección para buscar.'
        })

    direccion = direccion_original

    # Si el usuario no escribió "Córdoba", se agrega para que la búsqueda sea más precisa
    if 'córdoba' not in direccion.lower() and 'cordoba' not in direccion.lower():
        direccion = f'{direccion}, Córdoba, Argentina'

    # ---------- 1) Buscar las coordenadas de la dirección ----------
    # Se usa Nominatim (servicio gratuito de OpenStreetMap) para convertir dirección -> lat/lon
    try:
        respuesta = requests.get(
            'https://nominatim.openstreetmap.org/search',
            params={
                'q': direccion,                           # Texto a buscar
                'format': 'json',                         # Formato de la respuesta
                'countrycodes': 'ar',                     # Solo resultados de Argentina
                'viewbox': '-64.35,-31.30,-64.05,-31.55', # Rectángulo de la ciudad de Córdoba
                'bounded': 1                              # Obliga a buscar solo dentro del rectángulo
            },
            # Nominatim exige identificarse con un User-Agent (reemplazá por tu email real)
            headers={'User-Agent': 'app-emergencia/1.0 (tu_email@ejemplo.com)'},
            timeout=10,  # Si tarda más de 10 segundos, se corta
        )
        respuesta.raise_for_status()   # Lanza un error si el servidor respondió con código de falla (404, 500...)
        resultados = respuesta.json()  # Convierte la respuesta JSON en una lista de Python

    except (requests.ConnectionError, requests.Timeout):
        # Error de conexión o demasiado tiempo de espera: probablemente sin internet
        return render(request, 'hospitales_cercanos.html', {
            'error': 'No pudimos conectarnos para buscar tu dirección. '
                     'Revisá tu conexión a internet e intentá de nuevo en unos segundos.',
            'direccion': direccion_original,
        })

    except (requests.RequestException, ValueError):
        # Cualquier otro error de requests, o que la respuesta no sea un JSON válido
        return render(request, 'hospitales_cercanos.html', {
            'error': 'El servicio de direcciones no está disponible en este momento. '
                     'Probá de nuevo en un rato.',
            'direccion': direccion_original,
        })

    # Si la lista de resultados está vacía, la dirección no existe
    if not resultados:
        return render(request, 'hospitales_cercanos.html', {
            'error': 'No encontramos esa dirección. Probá con calle y número, por ejemplo: Av. Colón 500.',
            'direccion': direccion_original,
        })

    # Se toma el primer resultado (el más probable) y se guardan sus coordenadas como números
    lat_usuario = float(resultados[0]['lat'])
    lon_usuario = float(resultados[0]['lon'])

    # ---------- 2) Calcular distancias a los hospitales ----------
    lista_hospitales = []

    # Se recorren todos los hospitales guardados en la base de datos
    for hospital in Hospitales.objects.all():

        # Se buscan las coordenadas del hospital usando su nombre normalizado
        coordenadas = coordenadas_hospitales_normalizadas.get(
            normalizar(hospital.nombre)
        )

        # Si no hay coordenadas para ese nombre, se avisa por consola y se salta al siguiente
        if coordenadas is None:
            print('NO MATCHEA:', repr(hospital.nombre))
            continue

        lat_hospital, lon_hospital = coordenadas

        # Se agregan datos extra al objeto hospital (no se guardan en la BD, solo se usan en la plantilla)
        hospital.distancia = calcular_distancia(
            lat_usuario, lon_usuario,
            lat_hospital, lon_hospital
        )
        # Imagen del hospital; si no hay una asignada, se usa una por defecto
        hospital.imagen = imagenes_hospitales.get(hospital.nombre, 'img/hospital-default.jpg')
        hospital.lat = lat_hospital
        hospital.lon = lon_hospital
        # Texto para armar el enlace a Google Maps
        hospital.maps_query = f'{hospital.nombre} {hospital.ubicacion}, Córdoba, Argentina'
        lista_hospitales.append(hospital)

    # Si ningún hospital pudo cargarse, se muestra un error
    if not lista_hospitales:
        return render(request, 'hospitales_cercanos.html', {
            'error': 'No pudimos cargar los hospitales en este momento.',
            'direccion': direccion_original,
        })

    # Se ordena la lista de menor a mayor distancia (el más cercano primero)
    lista_hospitales.sort(key=lambda h: h.distancia)

    # ---------- 3) Mapa: si falla, igual se muestra la lista ----------
    mapa_url = None  # Si algo sale mal, queda en None y la plantilla no muestra el mapa

    try:
        # Carpeta donde se guardan las imágenes subidas/generadas (MEDIA_ROOT)
        carpeta = Path(settings.MEDIA_ROOT)
        carpeta.mkdir(parents=True, exist_ok=True)  # La crea si no existe

        # Se arma un nombre único según la ubicación del usuario
        # Así, si busca la misma dirección dos veces, reutiliza el mapa ya generado
        clave = hashlib.md5(
            f'{lat_usuario:.4f},{lon_usuario:.4f}'.encode()
        ).hexdigest()[:12]
        nombre_archivo = f'mapa_{clave}.png'
        ruta_imagen = carpeta / nombre_archivo

        # Solo se genera el mapa si todavía no existe
        if not ruta_imagen.exists():
            # Se crea un mapa de 600x400 píxeles que descarga los "mosaicos" de OpenStreetMap
            mapa = StaticMap(
                600, 400,
                url_template='https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                headers={'User-Agent': 'app-emergencia/1.0 (tu_email@ejemplo.com)'},
                tile_request_timeout=10,
            )
            # Punto ROJO: ubicación del usuario (ojo: staticmap usa el orden longitud, latitud)
            mapa.add_marker(CircleMarker((lon_usuario, lat_usuario), 'red', 12))

            # Puntos AZULES: uno por cada hospital
            for hospital in lista_hospitales:
                mapa.add_marker(CircleMarker((hospital.lon, hospital.lat), 'blue', 12))

            # Se dibuja el mapa y se guarda como imagen PNG
            mapa.render().save(ruta_imagen)

        # URL pública desde la que el navegador podrá mostrar la imagen
        mapa_url = settings.MEDIA_URL + nombre_archivo

    except Exception as e:
        # Cualquier falla (sin internet, error de escritura...) solo se imprime en consola
        print('Error al generar el mapa:', e)

    # Se muestra la página con el mapa, los hospitales ordenados y la dirección buscada
    return render(request, 'hospitales_cercanos.html', {
        'mapa_url': mapa_url,
        'hospitales_cercanos': lista_hospitales,
        'direccion': direccion_original,
    })


# ============================================================
# FORMULARIO DE EMERGENCIA -> TUTORIALES
# ============================================================

# Lista de reglas: (clave del tutorial, patrón de palabras a buscar)
# Cada patrón es una expresión regular. "|" significa "o" (cualquiera de esas palabras)
# \b marca el límite de una palabra (evita coincidencias dentro de otras palabras)
# .* significa "cualquier texto en el medio"
# El ORDEN IMPORTA: se revisan de arriba hacia abajo y gana la primera que coincide
# (por eso "rcp" e "infarto" van primero, por ser las más graves)
REGLAS_EMERGENCIA = [
    ('rcp', r'paro cardi|\bno respira|\brcp\b|reanim|dejo de respirar'),
    ('infarto', r'infarto|dolor (de|en el) pecho|opresion en el pecho'),
    ('acv', r'\bacv\b|ataque cerebral|derrame cerebral|cara caida|habla arrastrada|no puede hablar'),
    # Bebé atragantado va ANTES que atragantamiento general, para dar el tutorial específico
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

# Conjunto con todas las claves válidas (se arma recorriendo la lista de reglas)
# Sirve para validar que la clave que llega por la URL sea una de las permitidas
CLAVES_TUTORIALES = {clave for clave, _ in REGLAS_EMERGENCIA}


def detectar_emergencia(descripcion):
    # Recibe lo que escribió el usuario y devuelve la clave del tutorial que corresponde

    # Se normaliza (minúsculas y sin tildes) para que coincida con los patrones, que no tienen tildes
    texto = normalizar(descripcion)

    # Se prueban las reglas en orden
    for clave, patron in REGLAS_EMERGENCIA:
        # re.search busca el patrón en cualquier parte del texto
        if re.search(patron, texto):
            return clave  # Se devuelve la primera coincidencia

    # Si ninguna regla coincidió
    return None


def formulario_emergencia(request):
    # Muestra un formulario donde el usuario describe la emergencia

    if request.method == 'POST':

        # Texto que escribió el usuario
        descripcion = request.POST.get('descripcion', '')
        clave = detectar_emergencia(descripcion)

        if clave:
            # Se redirige a tutoriales con la clave en la URL:
            # "?abrir=clave" le indica a la plantilla qué tutorial abrir
            # "#clave" hace que el navegador baje hasta esa sección
            return redirect(f"{reverse('tutoriales')}?abrir={clave}#{clave}")

        # Si no se detectó ninguna emergencia, se avisa con ?no_encontrado=1
        return redirect(f"{reverse('tutoriales')}?no_encontrado=1")

    # Si es GET, se muestra el formulario
    return render(request, 'formulario_emergencia.html')


def tutoriales(request):
    # Muestra la página con todos los tutoriales de primeros auxilios

    # Se lee el parámetro "abrir" de la URL (ej: ?abrir=rcp). Si no viene, queda vacío
    abrir = request.GET.get('abrir', '')

    # Seguridad: si el valor no es una clave válida, se ignora
    if abrir not in CLAVES_TUTORIALES:
        abrir = ''

    return render(request, 'tutoriales.html', {
        'abrir': abrir,                                          # Tutorial a desplegar
        'no_encontrado': request.GET.get('no_encontrado') == '1',  # True si no se encontró coincidencia
    })


# ============================================================
# SOS
# ============================================================

def sos(request):
    # Permite enviar una alerta de emergencia (solo usuarios logueados)

    # Si no hay sesión iniciada, se redirige al login
    if 'id_usuario' not in request.session:
        return redirect('login')

    if request.method == 'POST':
        # [:100] y [:50] recortan el texto al máximo que admite cada columna de la BD
        descripcion = request.POST.get('descripcion', '').strip()[:100]
        direccion = request.POST.get('direccion', '').strip()[:50]

        # La descripción es obligatoria
        if not descripcion:
            return render(request, 'sos.html', {
                'error': 'Tenés que describir el peligro.',
                'direccion': direccion,  # Se devuelve la dirección para que no la tenga que escribir de nuevo
            })

        # Se guarda el accidente en la base de datos
        Accidentes.objects.create(
            id_usuario_id=request.session['id_usuario'],  # Usuario que envía la alerta (tomado de la sesión)
            direccion=direccion or None,                  # Si la dirección está vacía, se guarda como NULL
            fecha_hora=timezone.now(),                    # Fecha y hora actual
            descripcion=descripcion,
        )
        # Mensaje de confirmación que se mostrará en la página de inicio
        messages.success(request, 'Alerta enviada. Mantené la calma, la ayuda está en camino.')
        return redirect('inicio')

    # Si es GET, se muestra el formulario SOS
    return render(request, 'sos.html')