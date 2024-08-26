from django.db import models
from django.contrib.auth.models import User

class Usuario_I(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    dni = models.CharField(max_length=8, null=True)
    nombre = models.CharField(max_length=150)
    apellidos = models.CharField(max_length=150)
    esta_activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    foto_perfil = models.ImageField(upload_to='images/doctores/', null=True, blank=True)
    curriculum = models.FileField(upload_to='pdf/doctores/', null=True, blank=True)
    especialidad = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    celular = models.CharField(max_length=15)
    fecha_nacimiento = models.DateField(auto_now_add=True, null=True)
    direccion = models.CharField(max_length=150, null=True)
    genero = models.CharField(max_length=20, null=True, choices=[
        ('Masculino', 'Masculino'),
        ('Femenino', 'Femenino'),
        ('Otro', 'Otro'),
    ])

    def __str__(self):
        return self.nombre
    
class Paciente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    dni = models.CharField(max_length=8, null=True)
    nombre = models.CharField(max_length=150)
    apellidos = models.CharField(max_length=150)
    esta_activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    foto_perfil = models.ImageField(upload_to='images/pacientes/', null=True, blank=True)
    genero = models.CharField(max_length=20, choices=[
        ('Masculino', 'Masculino'),
        ('Femenino', 'Femenino'),
        ('Otro', 'Otro'),
    ])
    email = models.CharField(max_length=100)
    celular = models.CharField(max_length=15)
    direccion = models.CharField(max_length=255)
    ocupacion = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre 
    
class Servicio(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre
    
class Cita(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    motivo = models.TextField(max_length=500, blank=True, null=True)
    estado = models.CharField(max_length=20, choices=[
        ('programada', 'Programada'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    ], default='programada')
    notas = models.TextField(max_length=1000, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cita de {self.paciente.nombre} con {self.doctor.nombre}"

class Reporte(models.Model):
    cita = models.OneToOneField(Cita, on_delete=models.CASCADE)
    informacion = models.TextField()
    problemas = models.TextField(blank=True, null=True)
    recomendaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Reporte de {self.cita}"

class ReporteImagen(models.Model):
    reporte = models.ForeignKey(Reporte, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='images/reportes/', null=True, blank=True)

    def __str__(self):
        return f"Imagen para reporte {self.reporte.id}"
 
class Factura(models.Model):
    cita = models.OneToOneField(Cita, on_delete=models.CASCADE)
    numero_factura = models.CharField(max_length=50)
    fecha_emision = models.DateField()
    monto = models.DecimalField(max_digits=8, decimal_places=2)
    estado = models.CharField(max_length=20, choices=[
        ('cancelada', 'Cancelada'),
        ('en_deuda', 'En deuda'),
    ], default='en_deuda')

    def __str__(self):
        return f"Factura de {self.cita}"

class Pago(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE)
    monto_pagado = models.DecimalField(max_digits=8, decimal_places=2)
    fecha_pago = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Pago de {self.monto_pagado} para factura {self.factura}"

class Precio(models.Model):
    servicio = models.OneToOneField(Servicio, on_delete=models.CASCADE)
    precio = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"Precio de {self.servicio} - ${self.precio}"
