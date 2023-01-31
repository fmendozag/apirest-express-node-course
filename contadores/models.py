from django.db import models

# Create your models here.
class SisContadores(models.Model):
    codigo = models.CharField(db_column='Código', primary_key=True, max_length=50)
    valor = models.DecimalField(db_column='Valor', max_digits=18, decimal_places=0,default=0)

    def __str__(self):
        return '{}'.format(self.codigo)

    class Meta:
        verbose_name = 'Contador'
        verbose_name_plural = 'Contadores'
        managed = False
        db_table = 'SIS_CONTADORES'
