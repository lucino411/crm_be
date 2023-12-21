from django.db import models
from administration.organization.models import Organization


class ProductCategory(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField()
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    product_url = models.URLField(null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    

