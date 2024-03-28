from django.shortcuts import render
from .forms import InvoiceForm

def invoice_upload_view(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            print("Uploaded file:", uploaded_file.name)
    else:
        form = InvoiceForm()

    # invoices = Invoice.objects.all()
    return render(request, 'invoice_upload.html', {'form': form})
