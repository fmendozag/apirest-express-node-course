from django import forms
from cliente.models import CliClientes

class CliClientesForm(forms.ModelForm):
    class Meta:
        model = CliClientes
        fields = (
            'grupo',
            'zona',
            'vendedor',
            'division',
            'ruc',
            'ciudad',
            'direccion',
            'telefono1',
            'telefono2',
            'cupo',
            'cupo',
            'nombre',
            'credito',
            'foto',
            'email',
            'referencia',
            'gps_latitud',
            'gps_longitud',
            'dia_visita',
            'dia_entrega',
            'contacto',
            'nombre_comercial'
        )
        widgets = {
            'ruc': forms.TextInput(attrs={'required': True}),
            'telefono1': forms.TextInput(attrs={'required': True}),
            'nombre': forms.TextInput(attrs={'required': True,'placeholder':'Apellidos y nombres'}),
            'division': forms.Select(attrs={'required': True}),
            'grupo': forms.Select(attrs={'class': 'select2-design','required': True}),
            'ciudad': forms.Select(attrs={'class': 'select2-design','required': True}),
            'zona': forms.Select(attrs={'class': 'select2-design','required': True}),
            'direccion': forms.Textarea(attrs={'rows': '2','required': True}),
            'referencia': forms.Textarea(attrs={'rows': '2'}),
            'foto': forms.FileInput(attrs={
                'class': 'custom-file-input',
                'accept': ''
            }),
        }
