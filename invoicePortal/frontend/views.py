import os
import re
from django.shortcuts import render
from pathlib import Path

import openpyxl
from .forms import InvoiceForm
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse
from .utils.invoice_generate import generate_invoice_info_gpt
import uuid
import pandas as pd
from .models import Invoice, UploadProgress
from threading import Thread


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

    upload_id = str(uuid.uuid4())  # Generate a unique upload ID

    # Create an instance of UploadProgress
    upload_progress = UploadProgress.objects.create(
        upload_id=upload_id,
        total_files=len(files)
    )

    # Save the files to the local folder
    upload_folder = Path(settings.MEDIA_ROOT) / upload_id
    os.makedirs(upload_folder, exist_ok=True)

    for file in files:
        task_id = str(uuid.uuid4())  # Generate a unique task ID for each file
        file_name = f"{task_id}.pdf"  # Save the file with the task ID
        file_path = upload_folder / file_name
        with open(file_path, 'wb') as f:
            for chunk in file.chunks():
                f.write(chunk)

    # Start a new thread to process the files
    thread = Thread(target=process_files, args=(upload_id,))
    thread.start()

    # Return the upload ID to the client
    return Response({'upload_id': upload_id})


@api_view(['GET'])
def download_file(request, upload_id):
    file_name = f"result_{upload_id}.xlsx"
    upload_folder = Path(settings.MEDIA_ROOT) / upload_id
    file_path = upload_folder / file_name

    if not os.path.exists(file_path):
        return Response({'error': 'File not found or not ready'}, status=404)

    with open(file_path, 'rb') as fh:
        response = HttpResponse(fh.read(), content_type="application/pdf")
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


@api_view(['GET'])
def get_upload_progress(request):
    # Retrieve the latest upload progress from the database
    latest_progress = UploadProgress.objects.latest('id')

    progress = {
        'total_files': latest_progress.total_files,
        'processed_files': latest_progress.processed_files,
        'completed': latest_progress.completed
    }
    return Response(progress)


def process_files(upload_id):
    upload_progress = UploadProgress.objects.get(upload_id=upload_id)
    upload_folder = Path(settings.MEDIA_ROOT) / upload_id
    files = os.listdir(upload_folder)
    task_ids = [file.split('.')[0] for file in files if file.endswith('.pdf')]
    print("Number of files to process:", len(task_ids))

    batch_size = 5
    num_batches = (len(task_ids) + batch_size - 1) // batch_size

    def process_batch(batch_task_ids):
        for task_id in batch_task_ids:
            generate_invoice_info_gpt(task_id, upload_id, upload_folder)
            upload_progress.processed_files += 1
            upload_progress.save()
            print(f"Processed file {upload_progress.processed_files}/{len(task_ids)}")

    threads = []
    for i in range(num_batches):
        start_index = i * batch_size
        end_index = min(start_index + batch_size, len(task_ids))
        batch_task_ids = task_ids[start_index:end_index]
        thread = Thread(target=process_batch, args=(batch_task_ids,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    upload_progress.completed = True
    upload_progress.save()
