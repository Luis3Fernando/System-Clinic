from django.urls import path
from . import views

urlpatterns = [
    path('', views.Doctor_Home, name='doctor'),
    path('citasd/', views.Citas, name='citasd'),
    path('pacientes/', views.Pacientes, name='pacientes'),
    path('reportes/', views.Reportes, name='reportes'),
    path('agregar-cita-doctor/', views.Form_Citas, name='agregar-cita-doctor'),
    path('agregar-reporte/', views.Form_Reporte, name='agregar-reporte'),
    path('generate_reporte_pdf/<int:idReporte>/', views.generate_pdf, name='generate_reporte_pdf'),
    path('search-pacientes/', views.search_pacientes, name='search-pacientes'),
    path('seguimientod/', views.Seguimiento, name='seguimientod'),
    path('seguimientodc/<int:idPaciente>/', views.Seguimiento_Client, name='seguimientodc'),
    path('agregar_cita_ortodoncia/', views.agregar_cita_ortodoncia, name='agregar_cita_ortodoncia'),
    path('verificar_reporte/<int:cita_id>/', views.verificar_reporte, name='verificar_reporte'),
    path('obtener_imagenes_reporte/<int:idCita>/', views.obtener_imagenes_reporte, name='obtener_imagenes_reporte'),
]