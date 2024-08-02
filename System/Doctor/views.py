from django.shortcuts import render, redirect
from datetime import datetime, timedelta, time, date
from Home.models import *
from .utils import *
from django.db.models import Prefetch
from Client.utils import create_pdf
from django.http import HttpResponseForbidden, HttpResponse
from datetime import date

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
        estado = request.POST.get('estado')
        notas = request.POST.get('notas')
        
        try:
            doctor = Doctor.objects.get(user=request.user)
        except Doctor.DoesNotExist:
            doctor = None
        
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
            estado=estado,
            notas=notas
        )
        nueva_cita.save()
        
        return redirect('citasd')
    
    servicios = Servicio.objects.all()
    citas = Cita.objects.filter(doctor=doctor).select_related('paciente')
    pacientes = set(cita.paciente for cita in citas)
    
    context = {
        'pacientes': pacientes,
        'servicios': servicios
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

        errors = {}

        if not cita_id:
            errors['cita'] = "Este campo es obligatorio."
        if not informacion:
            errors['informacion'] = "Este campo es obligatorio."
        
        if not errors:
            cita = Cita.objects.get(id=cita_id)
            reporte = Reporte(
                cita=cita,
                informacion=informacion,
                problemas=problemas,
                recomendaciones=recomendaciones
            )
            reporte.save()
            return redirect('reportes') 
    else:
        errors = {}

    citas = Cita.objects.filter(doctor=doctor)

    context = {
        'citas': citas,
        'errors': errors
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