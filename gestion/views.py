from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Registro, ProductoUtilizado, Producto, Tratamiento, Consultorio, PacienteRecepcion, EstadoDoctor
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db.models import Q
from django.utils.dateparse import parse_date
from django.contrib.auth.models import User, Group
from django.http import JsonResponse, HttpResponse
import json
from django.template.loader import render_to_string
from django.utils.timezone import now, localdate
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

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


@login_required
def caja_panel_ajax(request):
    try:
        # Fecha actual segura para SQLite
        fecha_actual = localdate()

        registros = Registro.objects.filter(fecha=fecha_actual, estado='para_abonar').order_by('-fecha')

        html = render_to_string('gestion/_tabla_panel_caja.html', {'registros': registros}, request=request)
        return JsonResponse({'html': html})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@login_required
def panel_recepcion(request):
    if not request.user.groups.filter(name='Recepcion').exists():
        return HttpResponseForbidden("No tenés permiso para acceder a este panel.")
    return render(request, 'gestion/recepcion_panel.html')

@login_required
def estado_pacientes_ajax(request):
    pacientes = PacienteRecepcion.objects.order_by('-fecha_ingreso')

    grupo_doctores = Group.objects.get(name="Doctor")
    doctores = User.objects.filter(groups=grupo_doctores)

    for doctor in doctores:
        estado = getattr(doctor, 'estado_doctor', None)
        doctor.estado_display = estado.get_estado_display() if estado else 'Desconectado'
        doctor.estado_clase = estado.estado_clase() if estado else 'estado-desconectado'

    html = render_to_string('gestion/_tabla_pacientes.html', {
        'pacientes': pacientes,
        'doctores': doctores
    })

    return HttpResponse(html)




@csrf_exempt
@login_required
def ingresar_paciente_ajax(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        PacienteRecepcion.objects.create(
            nombre=data.get('nombre_apellido'),
            dni=data.get('dni', ''),
            fecha_nacimiento=data.get('fecha_nacimiento') or None,
            telefono=data.get('telefono', ''),
        )
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'Método no permitido'}, status=405)


@require_POST
@login_required
def eliminar_paciente(request, id):
    paciente = get_object_or_404(PacienteRecepcion, id=id)
    paciente.delete()
    return HttpResponse(status=204)

@require_POST
@login_required
def actualizar_estado_doctor(request):
    data = json.loads(request.body)
    nuevo_estado = data.get('estado')

    if nuevo_estado not in dict(EstadoDoctor.ESTADOS):
        return JsonResponse({'error': 'Estado inválido'}, status=400)

    estado, _ = EstadoDoctor.objects.get_or_create(doctor=request.user)
    estado.estado = nuevo_estado
    estado.save()

    return JsonResponse({'success': True})
