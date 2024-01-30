from django.db import models
from administration.organization.models import Organization


class Currency(models.Model):
    # Código ISO de la moneda, como 'USD', 'EUR', etc.
    code = models.CharField(max_length=3)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    def clean(self):
        super().clean()
        self.code = self.code.upper()

    def __str__(self):
        return self.code
    
    class Meta:
        verbose_name = 'Currency'
        verbose_name_plural = 'Currencies'
        ordering = ['code']
