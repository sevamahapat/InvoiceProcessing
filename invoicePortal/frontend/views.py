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

    upload_id = str(uuid.uuid4())  # Generate a unique upload ID

    # Create an instance of UploadProgress
    upload_progress = UploadProgress.objects.create(
        upload_id=upload_id,
        total_files=len(files)
    )

    for index, file in enumerate(files):
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

        generate_invoice_info_gpt(task_id, upload_id)

        # Update the progress
        upload_progress.processed_files = index + 1
        upload_progress.save()

    # Mark the upload as completed
    upload_progress.completed = True
    upload_progress.save()

    # Return the upload ID to the client
    return Response({'upload_id': upload_id})


@api_view(['GET'])
def download_file(request, upload_id):
    file_name = f"result_{upload_id}.xlsx"
    # file_name = f"{task_id}_processed.xlsx"
    file_path = Path(settings.MEDIA_ROOT) / file_name

    if not os.path.exists(file_path):
        return Response({'error': 'File not found or not ready'}, status=404)

    with open(file_path, 'rb') as fh:
        response = HttpResponse(fh.read(), content_type="application/pdf")
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response

    # # get all rows from the Invoice table and return them as xlsx file
    # invoices = Invoice.objects.all()
    # df = pd.DataFrame(list(invoices.values()))

    # # Create a BytesIO object to store the Excel file
    # from io import BytesIO
    # excel_file = BytesIO()

    # # Write the DataFrame to the BytesIO object as an Excel file
    # df.to_excel(excel_file, index=False)

    # # Create the HttpResponse object with the Excel file
    # response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    # response['Content-Disposition'] = 'attachment; filename="invoices.xlsx"'
    # response.write(excel_file.getvalue())
    # return response

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