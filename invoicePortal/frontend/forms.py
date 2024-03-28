from django import forms

class InvoiceForm(forms.Form):
    file = forms.FileField()
