from django.urls import path
from . import views

urlpatterns = [
    path('', views.Administrador, name='administrador'),
    path('usuarios/', views.Usuarios, name='usuarios'),
    path('doctores/', views.Doctores, name='doctores'),
    path('doctor/<int:id>/', views.Doctor_admin, name='doctor_admin'),
    path('cliente-admin/<int:id>/', views.Cliente, name='cliente-admin'),
    path('agregar-cliente-admin/', views.Form_Client, name='agregar-cliente-admin'),
    path('agregar-doctor/', views.Form_Doctor, name='agregar-doctor'),
    path('eliminar-cliente/<int:id>/', views.eliminar_cliente, name='eliminar-cliente'),
    path('eliminar-doctor/<int:id>/', views.eliminar_doctor, name='eliminar-doctor'),
    path('editar-cliente-admin/<int:id>/', views.editar_cliente, name='editar-cliente-admin'),
    path('actualizar-cliente/<int:id>/', views.actualizar_cliente, name='actualizar-cliente'),
    path('editar-doctor/<int:id>/', views.editar_doctor, name='editar-doctor'),
    path('actualizar-doctor/<int:id>/', views.actualizar_doctor, name='actualizar-doctor'),
    path('cv/<int:id>/', views.ver_cv, name='cv'),
]