import json
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from datetime import timedelta, date
from Home.models import Cita, Paciente, Factura, Doctor, Servicio
from .utils import *
from django.http import JsonResponse
from django.http import HttpResponseForbidden, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.timezone import now
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User
from django.contrib import messages

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
    facturas = Factura.objects.all().order_by('-fecha_emision')
    
    context={
        "facturas": facturas
    }
    return render(request, 'facturas-g.html', context)

@csrf_exempt
@require_POST
def actualizar_estado_factura(request, factura_id):
    try:
        factura = get_object_or_404(Factura, id=factura_id)
        data = json.loads(request.body)
        nuevo_estado = data.get('estado')

        if nuevo_estado not in ['en_deuda', 'cancelada']:
            return JsonResponse({'error': 'Estado no válido'}, status=400)
        
        factura.estado = nuevo_estado
        factura.save()
        
        return JsonResponse({'message': 'Estado actualizado'})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def Citas(request):
    citas = Cita.objects.all()
    contexto = preparar_contexto_citas(citas)
    return render(request, 'citas-g.html', contexto)

def AllCitas(request):
    citas = Cita.objects.all().order_by('-fecha')  # Ordena por fecha en orden descendente
    context = {
        "citas": citas
    }
    return render(request, "lista-citas.html", context)


def Cliente_perfil(request, id):
    client = get_object_or_404(Paciente, id=id)
    return render(request, 'cliente-g.html', {'client': client})
    

def Form_Cliente(request):
    if request.method == 'POST':
        try:
            dni = request.POST.get('dni')
            nombre = request.POST.get('nombre')
            apellidos = request.POST.get('apellido')
            genero = request.POST.get('genero')
            celular = request.POST.get('celular')
            email = request.POST.get('correo')
            direccion = request.POST.get('direccion')
            ocupacion = request.POST.get('ocupacion')

            foto_perfil = request.FILES.get('foto-perfil', None)

            username = f"{nombre.lower()}@{apellidos.lower().replace(' ', '')}"
            password = f"{dni}{nombre.lower()}"

            user = User.objects.create_user(username=username, password=password, email=email)
            user.first_name = nombre
            user.last_name = apellidos
            user.save()

            nuevo_cliente = Paciente(
                user=user,
                username=username,
                password=password,
                dni=dni,
                nombre=nombre,
                apellidos=apellidos,
                genero=genero,
                celular=celular,
                email=email,
                direccion=direccion,
                ocupacion=ocupacion,
                foto_perfil=foto_perfil
            )
            nuevo_cliente.save()

            messages.success(request, "Se agregó con éxito")
           
            enviar_correo(
                email, 
                "¡Bienvenido a Aless Dent!",
                f"Hola {nombre},\n\n"
                f"Nos complace darte la bienvenida a Aless Dent. A partir de ahora, tendrás acceso a nuestros servicios exclusivos.\n\n"
                f"Aquí tienes tus credenciales para acceder a tu cuenta:\n"
                f"• Usuario: {username}\n"
                f"• Contraseña: {password}\n\n"
                f"Por favor, mantén esta información segura y no la compartas con nadie.\n\n"
                f"Gracias por confiar en nosotros para el cuidado de tu salud dental.\n\n"
                f"Saludos cordiales,\n"
                f"El equipo de Aless Dent"
            )
           
            return redirect('clientes')

        except Exception as e:
            messages.error(request, f"Hubo un error inesperado: {str(e)}")
            return redirect('form-cliente')

    return render(request, 'form-cliente.html')

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
    if request.method == 'POST':
        try:
            paciente_id = request.POST.get('paciente')
            doctor_id = request.POST.get('doctor')
            servicio_id = request.POST.get('servicio')
            fecha = request.POST.get('fecha')
            hora_inicio = request.POST.get('hora_inicio')
            hora_fin = request.POST.get('hora_fin')
            motivo = request.POST.get('motivo')
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
                estado="programada",
                notas=notas
            )
            nueva_cita.save()

            messages.success(request, "Se agregó con éxito")
            return redirect('citas')

        except Exception as e:
            messages.error(request, f"Hubo un error inesperado: {str(e)}")
            return redirect('form-citas')
    
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
    today = now().date()
    start_date = today - timedelta(days=10)
    end_date = today + timedelta(days=10)

    if request.method == 'POST':
        try:
            monto = request.POST.get('monto')
            cita_id = request.POST.get('cita')
            estado = request.POST.get('estado')
            
            cita = Cita.objects.get(id=cita_id)
            numero_factura = generar_numero_factura()
            fecha_emision = today
            
            nueva_factura = Factura(
                numero_factura=numero_factura,
                fecha_emision=fecha_emision,
                monto=monto,
                cita=cita,
                estado=estado
            )
            nueva_factura.save()

            messages.success(request, "Se agregó con éxito")
            return redirect('facturas')

        except Exception as e:
            messages.error(request, f"Hubo un error inesperado: {str(e)}")
            return redirect('form-facturas')
    
    citas = Cita.objects.filter(
        estado__in=['programada', 'completada'],
        fecha__range=[start_date, end_date]
    ).exclude(
        factura__isnull=False
    ).exclude(
        estado='cancelada'
    )
    
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

def actualizar_estado_notas_cita(request, cita_id):
    if request.method == 'POST':
        cita = get_object_or_404(Cita, id=cita_id)
        data = json.loads(request.body)
        nuevo_estado = data.get('estado')
        nueva_nota = data.get('notas')
        if nuevo_estado in ['programada', 'completada', 'cancelada']:
            cita.estado = nuevo_estado
            cita.notas = nueva_nota
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