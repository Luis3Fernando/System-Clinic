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
]