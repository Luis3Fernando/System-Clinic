from django.urls import path
from . import views

urlpatterns = [
    path('', views.Recepcion, name='recepcion'),
    path('citas/', views.Citas, name='citas'),
    path('facturas/', views.Facturas, name='facturas'),
    path('clientes/', views.Clientes, name='clientes'),
    path('cliente/<int:id>/', views.Cliente_perfil, name='cliente'),
    path('editar-cliente/<int:id>/', views.editar_cliente, name='editar-cliente'),
    path('actualizar-cliente/<int:id>/', views.actualizar_cliente, name='actualizar-cliente'),
    path('agregar-paciente/', views.Form_Cliente, name='agregar-paciente'),
    path('agregar-cita/', views.Form_Citas, name='agregar-cita'),
    path('agregar-factura/', views.Form_Facturas, name='agregar-factura'),
    path('actualizar_estado_cita/<int:cita_id>/', views.actualizar_estado_cita, name='actualizar_estado_cita'),
    path('generate_boleta_pdf/<int:idFactura>/', views.generate_pdf, name='generate_boleta_pdf'),
]