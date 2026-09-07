from django.shortcuts import render, redirect
from .models import Usuario


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


def hospitales_cercanos(request):

    return render(request, 'hospitales_cercanos.html')


def formulario_emergencia(request):

    return render(request, 'formulario_emergencia.html')


def tutoriales(request):

    return render(request, 'tutoriales.html')