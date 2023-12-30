class LeadProduct(models.Model):
    lead = models.ForeignKey(
        Lead, related_name='lead_product', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='lead_product', on_delete=models.CASCADE)
    cotizacion_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.product.name
    

    class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    product_url = models.URLField(null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    