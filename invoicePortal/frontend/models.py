from django.db import models

class Invoice(models.Model):
    invoice_number = models.CharField(max_length=50, default="")
    supplier_name = models.CharField(max_length=100, default="")
    supplier_address_street1 = models.CharField(max_length=100, default="")
    supplier_address_street2 = models.CharField(max_length=100, blank=True, null=True)
    supplier_city = models.CharField(max_length=50, default="")
    supplier_state = models.CharField(max_length=50, default="")
    supplier_zip = models.CharField(max_length=20, default="")
    supplier_country = models.CharField(max_length=50, default="")
    ship_to_street1 = models.CharField(max_length=100, default="")
    ship_to_street2 = models.CharField(max_length=100, blank=True, null=True)
    ship_to_city = models.CharField(max_length=50, default="")
    ship_to_state = models.CharField(max_length=50, default="")
    ship_to_zip = models.CharField(max_length=20, default="")
    ship_to_country = models.CharField(max_length=50, default="")
    invoice_currency = models.CharField(max_length=10, default="")  # Assuming currency code is 3 characters long
    invoice_amount_incl_tax = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    invoice_tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    purchase_order = models.CharField(max_length=50, blank=True, null=True, default=0)

    def __str__(self):
        return self.invoice_number
    
    class Meta:
        app_label = 'frontend'
