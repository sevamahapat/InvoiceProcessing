from django.db import models

class Invoice(models.Model):
    vendor_name = models.CharField(max_length=100)
    invoice_number = models.CharField(max_length=100)
    date = models.DateField()
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.invoice_number
    
    class Meta:
        app_label = 'frontend'
