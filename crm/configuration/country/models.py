from django.db import models
from django.core.validators import RegexValidator
from administration.organization.models import Organization

class Country(models.Model):
    name = models.CharField(max_length=100, null=False,
                            blank=False, help_text="Nombre del país")
    code = models.CharField(
        max_length=6,
        null=False,
        blank=False,
        validators=[
            RegexValidator(
                r'^CO[A-Z]{3}$', 'El código debe empezar con CO seguido de tres mayúsculas')
        ]
    )
    is_selected = models.BooleanField(
        default=False, help_text="Indica si el país está seleccionado")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    def clean(self):
        super().clean()
        self.name = self.name.title()
        self.code = self.code.upper()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'
        ordering = ['name']
        constraints = [
            models.CheckConstraint(
                check=models.Q(code__regex=r'^CO[A-Z]{3}$'),
                name='El código debe empezar con CO seguido de tres mayúsculas'
            ),
            models.UniqueConstraint(
                fields=['code', 'organization'],
                name='La combinación de código y organización debe ser única.'
            ),
            models.UniqueConstraint(
                fields=['name', 'organization'],
                name='La combinación de nombre y organización debe ser única.'
            ),
        ]


'''
Ventajas de usar validators directamente en el campo:
Validación más específica: Al colocar la validación directamente en el campo, estás asociando la validación específicamente con ese campo. Esto puede ser útil si la validación es intrínseca al campo y no se aplica a la relación entre varios campos.
Reutilización en formularios: Si también estás utilizando formularios en tu aplicación, definir la validación directamente en el campo puede permitir la reutilización de la misma validación en los formularios de Django.

Ventajas de usar CheckConstraint:
Validación a nivel de base de datos: Las restricciones de comprobación se aplican a nivel de base de datos, lo que garantiza que los datos cumplan con las reglas de validación incluso si se insertan directamente a través de consultas de base de datos sin pasar por la capa de aplicación.
Mayor flexibilidad para reglas complejas: Si la regla de validación implica la relación entre varios campos o es más compleja, puede tener más sentido usar una restricción de comprobación, ya que puede involucrar más de un campo o requerir una lógica más avanzada.

Se pueden usar las dos tipos de validacion para una validacion mas completa.
'''
