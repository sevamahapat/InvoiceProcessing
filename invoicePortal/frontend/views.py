import os
from django.shortcuts import render
from pathlib import Path
from .forms import InvoiceForm
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse
from .utils.invoice_generate import generate_invoice_info_gpt
import uuid


def invoice_upload_view(request):
    form = InvoiceForm()
    return render(request, 'invoice_upload.html', {'form': form})


@api_view(['POST'])
def upload_file(request):
    if 'file' not in request.FILES:
        return Response({'error': 'No file provided'}, status=400)

    file = request.FILES['file']
    task_id = str(uuid.uuid4())  # Generate a unique task ID
    file_name = f"{task_id}.pdf"  # Save the file with the task ID

    # Construct the file path
    file_path = Path(settings.MEDIA_ROOT) / file_name

    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Save the file to the local folder
    with open(file_path, 'wb') as f:
        for chunk in file.chunks():
            f.write(chunk)

    # Start the background task (asynchronously)
    # process_file.delay(file_name, task_id)
    generate_invoice_info_gpt(file_path)

    # Return the task ID to the client
    return Response({'task_id': task_id})


@api_view(['GET'])
def download_file(request, task_id):
    file_name = "result.pdf"
    # file_name = f"{task_id}_processed.xlsx"
    file_path = Path(settings.MEDIA_ROOT) / file_name

    if not os.path.exists(file_path):
        return Response({'error': 'File not found or not ready'}, status=404)

    with open(file_path, 'rb') as fh:
        response = HttpResponse(fh.read(), content_type="application/pdf")
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response
