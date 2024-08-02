import json
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from datetime import time, date
from Home.models import *
from .utils import *
from django.http import JsonResponse
from django.http import HttpResponseForbidden, HttpResponse

def Recepcion(request):
    today = date.today()
    citas = Cita.objects.filter(
        fecha=today
    ).order_by('hora_inicio')

    citas_programadas = Cita.objects.filter(estado='programada', fecha=today).count()
    citas_completadas = Cita.objects.filter(estado='completada', fecha=today).count()
    citas_canceladas = Cita.objects.filter(estado='cancelada', fecha=today).count()

    contexto = {
        'citas_programadas': citas_programadas,
        'citas_completadas': citas_completadas,
        'citas_canceladas': citas_canceladas,
        'citas': citas,
    }
    return render(request, 'recepcion.html', contexto)

def Clientes(request):
    clientes = Paciente.objects.annotate(total_citas=Count('cita'))
        
    context = {
        'clients': clientes
    }
    return render(request, 'clientes-g.html', context)

def Facturas(request):
    facturas = Factura.objects.all()
    
    context={
        "facturas": facturas
    }
    return render(request, 'facturas-g.html', context)

def Citas(request):
    citas = Cita.objects.all()
    contexto = preparar_contexto_citas(citas)
    return render(request, 'citas-g.html', contexto)

def Cliente_perfil(request, id):
    client = get_object_or_404(Paciente, id=id)
    return render(request, 'cliente-g.html', {'client': client})
    

def Form_Cliente(request):
    return render(request, 'form-cliente.html')

def Form_Citas(request):
    if request.method == 'POST':
        paciente_id = request.POST.get('paciente')
        doctor_id = request.POST.get('doctor')
        servicio_id = request.POST.get('servicio')
        fecha = request.POST.get('fecha')
        hora_inicio = request.POST.get('hora_inicio')
        hora_fin = request.POST.get('hora_fin')
        motivo = request.POST.get('motivo')
        estado = request.POST.get('estado')
        notas = request.POST.get('notas')
        
        paciente = Paciente.objects.get(id=paciente_id)
        doctor = Doctor.objects.get(id=doctor_id)
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
        
        return redirect('citas')
    
    pacientes = Paciente.objects.all()
    doctores = Doctor.objects.all()
    servicios = Servicio.objects.all()
    
    context = {
        'pacientes': pacientes,
        'doctores': doctores,
        'servicios': servicios
    }
    return render(request, 'form-citas.html', context)

def Form_Facturas(request):
    if request.method == 'POST':
        monto = request.POST.get('monto')
        cita_id = request.POST.get('cita')
        estado = request.POST.get('estado')
        
        cita = Cita.objects.get(id=cita_id)
        numero_factura = generar_numero_factura
        fecha_emision = date.today()
        
        nueva_factura = Factura(
            numero_factura=numero_factura,
            fecha_emision=fecha_emision,
            monto=monto,
            cita=cita,
            estado=estado
        )
        nueva_factura.save()
        
        return redirect('facturas')
    
    citas = Cita.objects.all()
    
    context = {
        'citas': citas,
    }
    return render(request, 'form-facturas.html', context)

def editar_cliente(request, id):
    cliente = get_object_or_404(Paciente, id=id)
    return render(request, 'editar-cliente-g.html', {'cliente': cliente})

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
        return redirect('clientes') 
    return render(request, 'editar-cliente.html', {'cliente': cliente})


def actualizar_estado_cita(request, cita_id):
    if request.method == 'POST':
        cita = get_object_or_404(Cita, id=cita_id)
        data = json.loads(request.body)
        nuevo_estado = data.get('estado')
        if nuevo_estado in ['programada', 'completada', 'cancelada']:
            cita.estado = nuevo_estado
            cita.save()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Estado no válido'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

def generate_pdf(request, idFactura):
    fecha = date.today() 
    
    factura = Factura.objects.get(pk=idFactura)

    context = {
        'factura': factura,
        'fecha': fecha
    }

    ruta_template ='C:/Users/Luis Fernando/Documents/Unamba/Projects/System Clinic/System/static/pdf/boleta.html'
    
    #ruta_css = os.path.join(settings.STATIC_ROOT, 'styles', 'pdf_styles.css')
    ruta_css = ''

    ruta_pdf = create_pdf(ruta_template, context, rutacss=ruta_css)

    with open(ruta_pdf, 'rb') as pdf:
        response = HttpResponse(pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="resultado.pdf"'
        return response