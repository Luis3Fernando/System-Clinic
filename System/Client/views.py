from django.shortcuts import render, redirect, get_object_or_404
from datetime import date
from django.utils import timezone
from Home.models import Paciente, Cita, Factura, Reporte
from .utils import *
from django.http import HttpResponseForbidden, HttpResponse

def Client(request):
    today = date.today()
    ahora = timezone.now().time()
    
    if request.user.is_authenticated:
        try:
            paciente = Paciente.objects.get(user=request.user)
        except Paciente.DoesNotExist:
            paciente = None
            
        if paciente is not None:
            citas = Cita.objects.filter(
                    paciente=paciente,
                    fecha__gte=today,
            ).order_by('fecha', 'hora_inicio')
            
            citas_hoy = Cita.objects.filter(
            paciente=paciente,
            fecha=today,
            hora_inicio__gte=ahora,
            ).order_by('hora_inicio')
            
            citas_programadas = Cita.objects.filter(estado='programada', paciente=paciente).count()
            citas_completadas = Cita.objects.filter(estado='completada', paciente=paciente).count()
            citas_canceladas = Cita.objects.filter(estado='cancelada', paciente=paciente).count()
            
            citas = citas | citas_hoy
            context={
                'paciente': paciente,
                'citas': citas,
                'citas_programadas': citas_programadas,
                'citas_completadas': citas_completadas,
                'citas_canceladas': citas_canceladas,
            }
            return render(request, 'client.html', context)
        else:
            return redirect('login')
    else:
        return redirect('login')

def Facturas(request):
    if request.user.is_authenticated:
        try:
            paciente = Paciente.objects.get(user=request.user)
        except Paciente.DoesNotExist:
            paciente = None
            
        if paciente is not None:
            citas = Cita.objects.filter(paciente=paciente)
            facturas = Factura.objects.filter(cita__in=citas)
            
            context = {
                'facturas': facturas
            }
            return render(request, 'facturas.html', context)
        else:
            return redirect('login')
    else:
        return redirect('login')

    

def Citas(request):
    if request.user.is_authenticated:
        try:
            paciente = Paciente.objects.get(user=request.user)
            citas = Cita.objects.filter(paciente=paciente)
        except Paciente.DoesNotExist:
            paciente = None
            citas = []
    else:
        paciente = None
        citas = []

    contexto = preparar_contexto_citas(citas)
    return render(request, 'citas.html', contexto)

def historial(request):
    try:
        paciente = Paciente.objects.get(user=request.user)
    except Paciente.DoesNotExist:
        paciente = None

    if paciente:
        citas = paciente.cita_set.all()
        reportes = Reporte.objects.filter(cita__in=citas).order_by('-cita__fecha', '-cita__hora_inicio')
        ultimo_reporte = reportes.first() if reportes.exists() else None
        
        hoy = timezone.now().date()
        proximas_citas = citas.filter(fecha__gte=hoy).order_by('fecha', 'hora_inicio')
        proxima_cita = proximas_citas.first() if proximas_citas.exists() else None
    else:
        citas = None
        reportes = None
        ultimo_reporte = None
        proxima_cita = None

    context = {
        "reportes": reportes,
        "ultimo_reporte": ultimo_reporte,
        "proxima_cita": proxima_cita
    }
    return render(request, 'historial.html', context)

def Perfil(request):
    if request.user.is_authenticated:
        try:
            paciente = Paciente.objects.get(user=request.user)
        except Paciente.DoesNotExist:
            paciente = None
            
        if paciente is not None:
            return render(request, 'perfil.html', {'paciente': paciente})
        else:
            return redirect('login')
    else:
        return redirect('login')

def update_cliente(request, id):
    cliente = get_object_or_404(Paciente, id=id)
    return render(request, 'update-client.html', {'cliente': cliente})

def actualizar_cliente(request, id):
    cliente = get_object_or_404(Paciente, id=id)
    if request.method == 'POST':
        cliente.dni = request.POST['dni']
        cliente.nombre = request.POST['nombre']
        cliente.apellidos = request.POST['apellido']
        cliente.fecha_nacimiento = request.POST['fecha-nacimiento']
        cliente.genero = request.POST['genero']
        cliente.celular = request.POST['celular']
        cliente.email = request.POST['correo']
        cliente.direccion = request.POST['direccion']
        cliente.ocupacion = request.POST['ocupacion']
        if 'foto-perfil' in request.FILES:
            cliente.foto_perfil = request.FILES['foto-perfil']
        cliente.save()
        return redirect('perfil') 
    return render(request, 'actualizar-client.html', {'cliente': cliente})

def generate_pdf(request, idCita):
    try:
        paciente = Paciente.objects.get(user=request.user)
        cita = Cita.objects.get(id = idCita)
        reporte = Reporte.objects.get(cita = cita)
        
    except Paciente.DoesNotExist:
        return HttpResponseForbidden("No tienes permiso para ver esta página.")

    context = {
        'paciente': paciente,
        'cita': cita,
        'reporte': reporte
    }

    ruta_template ='C:/Users/Luis Fernando/Documents/Unamba/Projects/System Clinic/System/static/pdf/historial.html'
    
    #ruta_css = os.path.join(settings.STATIC_ROOT, 'styles', 'pdf_styles.css')
    ruta_css = ''

    ruta_pdf = create_pdf(ruta_template, context, rutacss=ruta_css)

    with open(ruta_pdf, 'rb') as pdf:
        response = HttpResponse(pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="resultado.pdf"'
        return response