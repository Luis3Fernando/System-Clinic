from django.urls import path
from . import views

urlpatterns = [
    path('', views.Client, name='client'),
    path('facturas-client/', views.Facturas, name='facturas-client'),
    path('citas/', views.Citas, name='citas'),
    path('historial/', views.historial, name='historial'),
    path('perfil/', views.Perfil, name='perfil'),
    path('update-cliente/<int:id>/', views.update_cliente, name='update-cliente'),
    path('actualizar-cliente-profile/<int:id>/', views.actualizar_cliente, name='actualizar-cliente-profile'),
    path('generate_pdf/<int:idCita>/', views.generate_pdf, name='generate_pdf'),
]