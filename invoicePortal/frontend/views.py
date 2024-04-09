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
    files = request.FILES.getlist('files')  # Get the list of files
    if not files:
        print(request)
        print("No files provided")
        return Response({'error': 'No files provided'}, status=400)

    task_ids = []  # Store generated task IDs for each file

    task_counter = 0

    for file in files:
        task_id = str(uuid.uuid4())  # Generate a unique task ID for each file
        task_ids.append(task_id)
        file_name = f"{task_id}.pdf"  # Save the file with the task ID

        # Construct the file path
        file_path = Path(settings.MEDIA_ROOT) / file_name

        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Save the file to the local folder
        with open(file_path, 'wb') as f:
            for chunk in file.chunks():
                f.write(chunk)

        # Here, you might want to process each file asynchronously
        # For example: process_file.delay(file_name, task_id)
        # Or if processing synchronously, just call the function
        # Example: generate_invoice_info_gpt(task_id)
        task_counter += 1
        print(f"Processing task_id {task_id}, progress: {task_counter}/{len(files)}")
        generate_invoice_info_gpt(task_id)

    # Return the task IDs to the client
    return Response({'task_ids': task_ids})


@api_view(['GET'])
def download_file(request, task_id):
    file_name = "result.xlsx"
    # file_name = f"{task_id}_processed.xlsx"
    file_path = Path(settings.MEDIA_ROOT) / file_name

    if not os.path.exists(file_path):
        return Response({'error': 'File not found or not ready'}, status=404)

    with open(file_path, 'rb') as fh:
        response = HttpResponse(fh.read(), content_type="application/pdf")
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response
