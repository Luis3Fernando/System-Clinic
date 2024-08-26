from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime, timedelta, time, date
from Home.models import *
from .utils import *
from django.db.models import Prefetch
from Client.utils import create_pdf
from django.http import HttpResponseForbidden, HttpResponse
from datetime import date
from django.http import JsonResponse
from django.contrib import messages

def Doctor_Home(request):
    today = date.today()
    
    if request.user.is_authenticated:
        try:
            doctor = Doctor.objects.get(user=request.user)
        except Doctor.DoesNotExist:
            doctor = None
            
        if doctor is not None:
            citas = Cita.objects.filter(
                fecha=today, doctor=doctor
            ).order_by('hora_inicio')
            
            citas_programadas = Cita.objects.filter(estado='programada', fecha=today, doctor=doctor).count()
            citas_completadas = Cita.objects.filter(estado='completada',fecha=today, doctor=doctor).count()
            citas_canceladas = Cita.objects.filter(estado='cancelada', fecha=today,  doctor=doctor).count()
            
            context={
                'doctor': doctor,
                'citas': citas,
                'citas_programadas': citas_programadas,
                'citas_completadas': citas_completadas,
                'citas_canceladas': citas_canceladas,
            }
            return render(request, 'doctor.html', context)
        else:
            return redirect('login')
    else:
        return redirect('login')

def Pacientes(request):
    if request.user.is_authenticated:
        try:
            doctor = Doctor.objects.get(user=request.user)
        except Doctor.DoesNotExist:
            doctor = None
            
        if doctor is not None:
            citas = Cita.objects.filter(doctor=doctor).select_related('paciente')
            pacientes = set(cita.paciente for cita in citas)
            
            context = {
                'pacientes': pacientes
            }
            return render(request, 'pacientes.html', context)
        else:
            return redirect('login')
    else:
        return redirect('login')

def Citas(request):
    if request.user.is_authenticated:
        try:
            doctor = Doctor.objects.get(user=request.user)
            citas = Cita.objects.filter(doctor=doctor)
        except Doctor.DoesNotExist:
            doctor = None
            citas = []
    else:
        doctor = None
        citas = []

    contexto = preparar_contexto_citas(citas)
    return render(request, 'citas-doctor.html', contexto)

def Reportes(request):
    try:
        doctor = Doctor.objects.get(user=request.user)
        reportes = Reporte.objects.filter(cita__doctor=doctor)
    except Doctor.DoesNotExist:
        doctor = None
        reportes = None
        
    context = {
        'reportes': reportes,
    }
    return render(request, 'reportes.html', context)

def search_pacientes(request):
    query = request.GET.get('q', '')
    pacientes = Paciente.objects.filter(
        nombre__icontains=query
    ) | Paciente.objects.filter(
        apellidos__icontains=query
    )
    print("lo pacientes encontrados: ", pacientes)
    pacientes_data = [
        {'id': paciente.id, 'nombre': paciente.nombre, 'apellidos': paciente.apellidos}
        for paciente in pacientes
    ]
    return JsonResponse({'pacientes': pacientes_data})

def Form_Citas(request):
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        doctor = None

    if request.method == 'POST':
        paciente_id = request.POST.get('paciente')
        servicio_id = request.POST.get('servicio')
        fecha = request.POST.get('fecha')
        hora_inicio = request.POST.get('hora_inicio')
        hora_fin = request.POST.get('hora_fin')
        motivo = request.POST.get('motivo')
        notas = request.POST.get('notas')

        try:
            paciente = Paciente.objects.get(id=paciente_id)
            servicio = Servicio.objects.get(id=servicio_id)
            nueva_cita = Cita(
                paciente=paciente,
                doctor=doctor,
                servicio=servicio,
                fecha=fecha,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                motivo=motivo,
                estado="programada",
                notas=notas
            )
            nueva_cita.save()
            messages.success(request, "La cita se ha programado con éxito.")
            return redirect('citasd')
        except Paciente.DoesNotExist:
            messages.error(request, "El paciente seleccionado no existe.")
        except Servicio.DoesNotExist:
            messages.error(request, "El servicio seleccionado no existe.")
        except Exception as e:
            messages.error(request, f"Hubo un error al guardar la cita: {str(e)}")

    servicios = Servicio.objects.all()
    citas = Cita.objects.filter(doctor=doctor).select_related('paciente')
    pacientes = set(cita.paciente for cita in citas)

    context = {
        'pacientes': pacientes,
        'servicios': servicios,
    }
    return render(request, 'form-citas-doctor.html', context)

def Form_Reporte(request):
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        return redirect('login')

    if request.method == 'POST':
        cita_id = request.POST.get('cita')
        informacion = request.POST.get('informacion')
        problemas = request.POST.get('problemas')
        recomendaciones = request.POST.get('recomendaciones')

        try:
            cita = Cita.objects.get(id=cita_id)
            reporte = Reporte(
                cita=cita,
                informacion=informacion,
                problemas=problemas,
                recomendaciones=recomendaciones
            )
            reporte.save()

            cita.estado = 'completada'
            cita.save()

            imagen_files = request.FILES.getlist('imagenes')
            for imagen_file in imagen_files:
                ReporteImagen.objects.create(reporte=reporte, imagen=imagen_file)

            messages.success(request, "El reporte se ha guardado con éxito.")
            return redirect('reportes')
        except Cita.DoesNotExist:
            messages.error(request, "La cita seleccionada no existe.")
        except Exception as e:
            messages.error(request, f"Hubo un error al guardar el reporte: {str(e)}")

    citas = Cita.objects.filter(doctor=doctor)

    context = {
        'citas': citas,
    }
    return render(request, 'form-reporte.html', context)

def generate_pdf(request, idReporte):
    fecha = date.today() 
    try:
        doctor = Doctor.objects.get(user=request.user)
        reporte = Reporte.objects.get(pk = idReporte)
        
    except Paciente.DoesNotExist:
        return HttpResponseForbidden("No tienes permiso para ver esta página.")

    context = {
        'reporte': reporte,
        'doctor': doctor,
        'fecha': fecha
    }

    ruta_template ='C:/Users/Luis Fernando/Documents/Unamba/Projects/System Clinic/System/static/pdf/reporte.html'
    
    #ruta_css = os.path.join(settings.STATIC_ROOT, 'styles', 'pdf_styles.css')
    ruta_css = ''

    ruta_pdf = create_pdf(ruta_template, context, rutacss=ruta_css)

    with open(ruta_pdf, 'rb') as pdf:
        response = HttpResponse(pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="resultado.pdf"'
        return response
    
def Seguimiento(request):
    if request.user.is_authenticated:
        try:
            doctor = Doctor.objects.get(user=request.user)
        except Doctor.DoesNotExist:
            doctor = None
            
        if doctor is not None:
            citas = Cita.objects.filter(doctor=doctor, servicio__nombre="Ortodoncia").select_related('paciente')
            pacientes = set(cita.paciente for cita in citas)
            
            context = {
                'pacientes': pacientes
            }
            return render(request, "doctor-seguimiento.html", context)
        else:
            return redirect('login')
    else:
        return redirect('login')
    
def Seguimiento_Client(request, idPaciente):
    paciente = get_object_or_404(Paciente, id=idPaciente)
    
    # Filtrar todas las citas de Ortodoncia para el paciente, ordenadas por fecha
    citas = Cita.objects.filter(
        paciente=paciente,
        servicio__nombre='Ortodoncia'
    ).order_by('fecha')
    
    # Obtener el último reporte y las imágenes asociadas a él
    ultimo_reporte = Reporte.objects.filter(cita__in=citas).last()
    imagenes = ultimo_reporte.imagenes.all() if ultimo_reporte else []
    
    context = {
        'paciente': paciente,
        'reportes': citas,
        'imagenes': imagenes,
        'no_reportes': not citas.exists(),
    }
    return render(request, 'seguimiento_client.html', context)

def obtener_imagenes_reporte(request, idCita):
    reporte = Reporte.objects.filter(cita_id=idCita).last()
    imagenes = []

    if reporte:
        imagenes = [{'imagen': request.build_absolute_uri(imagen.imagen.url)} for imagen in reporte.imagenes.all()]

    return JsonResponse({'imagenes': imagenes})


def agregar_cita_ortodoncia(request):
    if request.method == 'POST':
        paciente_id = request.POST.get('paciente')

        doctor = Doctor.objects.filter(user=request.user).first()
        if not doctor:
            messages.error(request, "No se encontró un doctor asociado a este usuario.")
            return redirect('seguimientod')

        servicio, created = Servicio.objects.get_or_create(nombre='Ortodoncia')

        fecha = request.POST.get('fecha')
        hora_inicio = request.POST.get('hora_inicio')
        hora_fin = request.POST.get('hora_fin')
        motivo = request.POST.get('motivo')
        notas = request.POST.get('notas')

        paciente = get_object_or_404(Paciente, id=paciente_id)

        nueva_cita = Cita(
            paciente=paciente,
            doctor=doctor,
            servicio=servicio,
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            motivo=motivo,
            notas=notas
        )
        nueva_cita.save()

        messages.success(request, "Cita de ortodoncia creada exitosamente.")
        return redirect('seguimientodc', idPaciente=paciente_id)

    return redirect('seguimientod')


def verificar_reporte(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)
    try:
        reporte = Reporte.objects.get(cita=cita)
        return redirect('generate_reporte_pdf', idReporte=reporte.id)
    except Reporte.DoesNotExist:
        messages.error(request, "No hay reporte creado para esta cita.")
        return redirect('seguimientod')

