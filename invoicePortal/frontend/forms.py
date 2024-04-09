from django import forms
from .models import Invoice

class InvoiceForm(forms.Form):
    file = forms.FileField()
    
