from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Registro, ProductoUtilizado, Producto, Tratamiento, Consultorio
from django.contrib import messages
from django.db.models import Q
from django.utils.dateparse import parse_date
from django.contrib.auth.models import User, Group

@login_required
def home(request):

    if request.user.groups.filter(name='Caja').exists():
        return redirect('panel_caja')
    else:
        return redirect('panel_doctor')

@login_required
def panel_doctor(request):
    if request.method == 'POST':
        nombre_paciente = request.POST.get('nombre_paciente')
        tratamiento_nombre = request.POST.get('tratamiento_nombre')
        consultorio_nombre = request.POST.get('consultorio_nombre')

        # Buscar o crear Tratamiento
        tratamiento, _ = Tratamiento.objects.get_or_create(nombre=tratamiento_nombre)

        # Buscar o crear Consultorio
        consultorio, _ = Consultorio.objects.get_or_create(nombre=consultorio_nombre)

        # Crear Registro
        registro = Registro.objects.create(
            nombre_paciente=nombre_paciente,
            tratamiento=tratamiento,
            doctor=request.user,
            consultorio=consultorio
        )

        # Procesar productos y cantidades
        producto_nombres = request.POST.getlist('producto_nombre')
        cantidades = request.POST.getlist('cantidad')

        for nombre, cantidad in zip(producto_nombres, cantidades):
            if nombre.strip() == '' or cantidad.strip() == '':
                continue  # Ignorar productos vacíos

            producto, _ = Producto.objects.get_or_create(nombre=nombre)
            ProductoUtilizado.objects.create(
                registro=registro,
                producto=producto,
                cantidad=int(cantidad)
            )
        messages.success(request, "El producto fue enviado correctamente a Caja.")
        return redirect('panel_doctor')

    productos = Producto.objects.all()
    tratamientos = Tratamiento.objects.all()
    consultorios = Consultorio.objects.all()
    return render(request, 'gestion/doctor_panel.html', {
        'productos': productos,
        'tratamientos': tratamientos,
        'consultorios': consultorios,
    })
@login_required
def panel_caja(request):
    hoy = timezone.now().date()
    registros = Registro.objects.filter(fecha=hoy, estado='para_abonar')

    if request.method == 'POST':
        registro_id = request.POST.get('registro_id')
        Registro.objects.filter(id=registro_id).update(estado='abonado')
        return redirect('panel_caja')

    return render(request, 'gestion/caja_panel.html', {'registros': registros})


@login_required
def historial_caja(request):
    registros = Registro.objects.filter(estado='abonado').order_by('-fecha')

    producto_nombre = request.GET.get('producto')
    doctor_id = request.GET.get('doctor')
    fecha_inicio = request.GET.get('desde')
    fecha_fin = request.GET.get('hasta')

    # Aplicar filtros
    if producto_nombre:
        registros = registros.filter(productoutilizado__producto__nombre=producto_nombre)
    if doctor_id:
        registros = registros.filter(doctor__id=doctor_id)
    if fecha_inicio:
        registros = registros.filter(fecha__gte=parse_date(fecha_inicio))
    if fecha_fin:
        registros = registros.filter(fecha__lte=parse_date(fecha_fin))

    # Datos para los filtros
    productos = Producto.objects.all().order_by('nombre')
    grupo_doctores = Group.objects.get(name="Doctor")  # Asegurate de tener este grupo
    doctores = User.objects.filter(groups=grupo_doctores)

    return render(request, 'gestion/historial.html', {
        'registros': registros,
        'productos': productos,
        'doctores': doctores,
        'producto_filtro': producto_nombre or '',
        'doctor_filtro': int(doctor_id) if doctor_id else '',
        'desde': fecha_inicio or '',
        'hasta': fecha_fin or '',
    })

@login_required
def historial_doctor(request):
    registros = Registro.objects.filter(doctor=request.user).order_by('-fecha')
    return render(request, 'gestion/doctor_historial.html', {'registros': registros})