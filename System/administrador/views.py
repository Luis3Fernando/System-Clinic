from django.shortcuts import render, redirect, get_object_or_404
from Home.models import *
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User
from django.db.models import Count
from datetime import datetime, timedelta
from django.db.models import Sum
from django.contrib import messages
from recepcion.utils import *

def formatear_fecha_actual():
    meses = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]
    hoy = datetime.today()  
    mes = meses[hoy.month - 1]  
    return f"{mes} {hoy.day} de {hoy.year}"

def Administrador(request):
    # Cálculo de totales de doctores y pacientes
    total_doctores = Doctor.objects.count()
    total_pacientes = Paciente.objects.count()

    # Cálculo de citas
    citas_programadas = Cita.objects.filter(estado='programada').count()
    citas_completadas = Cita.objects.filter(estado='completada').count()
    citas_canceladas = Cita.objects.filter(estado='cancelada').count()
    
    # Cálculo de ingresos
    hoy = datetime.now().date()
    fecha_inicio_mes = hoy.replace(day=1)
    fecha_inicio_semana = hoy - timedelta(days=hoy.weekday())
    fecha_inicio_ultimo_mes = hoy - timedelta(days=30)
    
    ingresos_totales = Factura.objects.filter(estado='cancelada').aggregate(total=Sum('monto'))['total'] or 0
    ingresos_ultimo_mes = Factura.objects.filter(estado='cancelada', fecha_emision__gte=fecha_inicio_mes).aggregate(total=Sum('monto'))['total'] or 0
    ingresos_ultima_semana = Factura.objects.filter(estado='cancelada', fecha_emision__gte=fecha_inicio_semana).aggregate(total=Sum('monto'))['total'] or 0
    ingresos_hoy = Factura.objects.filter(estado='cancelada', fecha_emision=hoy).aggregate(total=Sum('monto'))['total'] or 0

    # Cálculo de citas por día
    citas_diarias = Cita.objects.filter(fecha__gte=fecha_inicio_semana).values('fecha').annotate(total=Count('id')).order_by('fecha')
    
    # Formateo de días de la semana
    dias = []
    for i in range(5):
        dia = hoy - timedelta(days=i)
        if dia.weekday() == 6:  # Excluir domingos
            continue
        dias.append(dia.strftime('%A'))
    
    # Preparar datos para el histograma
    citas_por_dia = {dia: 0 for dia in dias}
    for cita in citas_diarias:
        fecha_dia = cita['fecha'].strftime('%A')
        if fecha_dia in citas_por_dia:
            citas_por_dia[fecha_dia] += cita['total']

    # Ordenar días para el histograma
    dias_ordenados = [dia for dia in dias if dia in citas_por_dia]

    context = {
        'total_doctores': total_doctores,
        'total_pacientes': total_pacientes,
        'citas_programadas': citas_programadas,
        'citas_completadas': citas_completadas,
        'citas_canceladas': citas_canceladas,
        'fecha': formatear_fecha_actual(),
        'ingresos_totales': ingresos_totales,
        'ingresos_ultimo_mes': ingresos_ultimo_mes,
        'ingresos_ultima_semana': ingresos_ultima_semana,
        'ingresos_hoy': ingresos_hoy,
        'citas_por_dia': citas_por_dia,
        'dias_ordenados': dias_ordenados,
    }
    return render(request, 'administrador.html', context)

def Usuarios(request):
    clientes = Paciente.objects.annotate(total_citas=Count('cita'))
        
    context = {
        'clients': clientes
    }
    return render(request, 'usuarios.html' , context)

def Doctores(request):
    doctors = Doctor.objects.annotate(total_citas=Count('cita'))
    
    return render(request, 'doctores.html', {'doctors': doctors})

def Doctor_admin(request, id):
    doctor = get_object_or_404(Doctor, id=id)
    return render(request, 'admin-doctor.html', {'doctor': doctor})

def ver_cv(request, id):
    doctor = get_object_or_404(Doctor, id=id)
    return render(request, 'ver_cv.html', {'doctor': doctor})

def Cliente(request, id):
    client = get_object_or_404(Paciente, id=id)
    return render(request, 'admin-client.html', {'client': client})

def Form_Doctor(request):
    if request.method == 'POST':
        try:
            dni = request.POST['dni']
            nombre = request.POST['nombre']
            apellidos = request.POST['apellido']
            genero = request.POST['genero']
            celular = request.POST['celular']
            email = request.POST['correo']
            direccion = request.POST['direccion']
            especialidad = request.POST['especialidad']

            if 'foto-perfil' in request.FILES:
                foto_perfil = request.FILES['foto-perfil']
                fs = FileSystemStorage()
                foto_perfil_name = fs.save(foto_perfil.name, foto_perfil)
            else:
                foto_perfil_name = None

            if 'curriculum' in request.FILES:
                curriculum = request.FILES['curriculum']
                fs = FileSystemStorage()
                curriculum_name = fs.save(curriculum.name, curriculum)
            else:
                curriculum_name = None

            username = f"{nombre.lower()}@{apellidos.lower().replace(' ', '')}"
            password = f"{dni}{nombre.lower()}"

            user = User.objects.create_user(username=username, password=password, email=email)
            user.first_name = nombre
            user.last_name = apellidos
            user.save()

            doctor = Doctor(
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
                especialidad=especialidad,
                foto_perfil=foto_perfil_name,
                curriculum=curriculum_name
            )
            doctor.save()
            enviar_correo(
                email, 
                "¡Bienvenido a Aless Dent!",
                f"Hola Dr./Dra. {nombre},\n\n"
                f"Nos complace darte la bienvenida al equipo de Aless Dent. A partir de ahora, formarás parte de nuestro equipo dedicado a brindar un excelente servicio dental.\n\n"
                f"Aquí tienes tus credenciales para acceder a tu cuenta:\n"
                f"• Usuario: {username}\n"
                f"• Contraseña: {password}\n\n"
                f"Por favor, mantén esta información segura y no la compartas con nadie.\n\n"
                f"Estamos emocionados de contar contigo y esperamos que tengas una experiencia gratificante con nosotros.\n\n"
                f"Saludos cordiales,\n"
                f"El equipo de Aless Dent"
            )

            messages.success(request, "Doctor agregado con éxito")
            return redirect('doctores')

        except Exception as e:
            messages.error(request, f"Hubo un error al agregar el doctor: {str(e)}")
            return redirect('form-doctor')

    return render(request, 'form-doctor.html')


def Form_Client(request):
    if request.method == 'POST':
        try:
            dni = request.POST['dni']
            nombre = request.POST['nombre']
            apellidos = request.POST['apellido']
            genero = request.POST['genero']
            celular = request.POST['celular']
            email = request.POST['correo']
            direccion = request.POST['direccion']
            ocupacion = request.POST['ocupacion']

            if 'foto-perfil' in request.FILES:
                foto_perfil = request.FILES['foto-perfil']
                fs = FileSystemStorage()
                foto_perfil_name = fs.save(foto_perfil.name, foto_perfil)
            else:
                foto_perfil_name = None

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
                foto_perfil=foto_perfil_name
            )
            nuevo_cliente.save()
            messages.success(request, "Cliente agregado con éxito")
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
            return redirect('usuarios')

        except Exception as e:
            messages.error(request, f"Hubo un error al agregar el cliente: {str(e)}")
            return redirect('form-client')

    return render(request, 'form-client.html')

def eliminar_cliente(request, id):
    if request.method == "POST":
        try:
            cliente = get_object_or_404(Paciente, id=id)
            cliente.delete()
            messages.success(request, "Cliente eliminado con éxito")
            return redirect('usuarios')
        except Exception as e:
            messages.error(request, f"Hubo un error al eliminar el cliente: {str(e)}")
            return redirect('usuarios')
    else:
        return HttpResponseForbidden("No tienes permiso para realizar esta acción.")

    
def eliminar_doctor(request, id):
    if request.method == "POST":
        try:
            doctor = get_object_or_404(Doctor, id=id)
            doctor.delete()
            messages.success(request, "Doctor eliminado con éxito")
            return redirect('doctores')
        except Exception as e:
            messages.error(request, f"Hubo un error al eliminar el doctor: {str(e)}")
            return redirect('doctores')
    else:
        return HttpResponseForbidden("No tienes permiso para realizar esta acción.")

    
def editar_cliente(request, id):
    cliente = get_object_or_404(Paciente, id=id)
    return render(request, 'editar-cliente.html', {'cliente': cliente})


def actualizar_cliente(request, id):
    cliente = get_object_or_404(Paciente, id=id)
    if request.method == 'POST':
        try:
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
            messages.success(request, "Cliente actualizado con éxito")
            return redirect('usuarios')
        except Exception as e:
            messages.error(request, f"Hubo un error al actualizar el cliente: {str(e)}")
            return redirect('editar-cliente', id=id)
    return render(request, 'editar-cliente.html', {'cliente': cliente})


def editar_doctor(request, id):
    doctor = get_object_or_404(Doctor, id=id)
    return render(request, 'editar-doctor.html', {'doctor': doctor})

def actualizar_doctor(request, id):
    doctor = get_object_or_404(Doctor, id=id)
    if request.method == 'POST':
        try:
            doctor.dni = request.POST['dni']
            doctor.nombre = request.POST['nombre']
            doctor.apellidos = request.POST['apellido']
            doctor.genero = request.POST['genero']
            doctor.celular = request.POST['celular']
            doctor.email = request.POST['correo']
            doctor.direccion = request.POST['direccion']
            doctor.especialidad = request.POST['especialidad']
            if 'foto-perfil' in request.FILES:
                doctor.foto_perfil = request.FILES['foto-perfil']
            if 'curriculum' in request.FILES:
                doctor.curriculum = request.FILES['curriculum']
            doctor.save()
            messages.success(request, "Doctor actualizado con éxito")
            return redirect('doctores')
        except Exception as e:
            messages.error(request, f"Hubo un error al actualizar el doctor: {str(e)}")
            return redirect('editar-doctor', id=id)
    return render(request, 'editar-doctor.html', {'doctor': doctor})


