from django import forms
from Home.models import Cita

class CitaEstadoForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['estado']
        widgets = {
            'estado': forms.RadioSelect(choices=[
                ('programada', 'Programada'),
                ('completada', 'Completada'),
                ('cancelada', 'Cancelada')
            ])
        }
