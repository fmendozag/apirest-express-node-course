from django import forms

from inventario.models import InvFisico


class InvTomaFisicoForm(forms.ModelForm):
    class Meta:
        model = InvFisico
        fields = (
            'bodega',
            'fecha',
            'detalle',
            'division',
            'procesado'
        )
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date','required': True}),
            'division': forms.Select(attrs={'required': True}),
            'bodega': forms.Select(attrs={'class': 'select2-design','required': True}),
        }
