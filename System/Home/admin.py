from django.contrib import admin
from .models import Doctor, Paciente, Cita, Reporte, Factura, Pago, Servicio, Precio, ReporteImagen

admin.site.register(ReporteImagen)
admin.site.register(Doctor)
admin.site.register(Paciente)
admin.site.register(Cita)
admin.site.register(Reporte)
admin.site.register(Factura)
admin.site.register(Pago)
admin.site.register(Servicio)
admin.site.register(Precio)