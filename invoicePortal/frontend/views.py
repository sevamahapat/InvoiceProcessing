from django.core.files.storage import default_storage
from django.shortcuts import render
from .forms import InvoiceForm
from django.http import HttpResponse
from azure.storage.blob import generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta
from django.conf import settings


def invoice_upload_view(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            if file.content_type != 'application/pdf':
                return HttpResponse("Please upload a PDF file.", status=400)

            file_name = default_storage.save(file.name, file)
            sas_url = generate_sas_url(settings.AZURE_CONTAINER, file_name)
            print("Uploaded file name and URL:", file_name, sas_url)
    else:
        form = InvoiceForm()

    # invoices = Invoice.objects.all()
    return render(request, 'invoice_upload.html', {'form': form})


def generate_sas_url(container_name, blob_name):
    sas_token = generate_blob_sas(account_name=settings.AZURE_ACCOUNT_NAME,
                                  container_name=container_name,
                                  blob_name=blob_name,
                                  account_key=settings.AZURE_ACCOUNT_KEY,
                                  permission=BlobSasPermissions(read=True),
                                  expiry=datetime.utcnow() + timedelta(hours=1))  # Token valid for 1 hour
    return f"https://{settings.AZURE_ACCOUNT_NAME}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"
