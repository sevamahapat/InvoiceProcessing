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
from .models import Invoice

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
        result_data = generate_invoice_info_gpt(task_id)
        invoice_amount_incl_tax = result_data['Invoice amount (Incl tax)'].iloc[0]
        if invoice_amount_incl_tax == 'N/A' or invoice_amount_incl_tax == '':
            invoice_amount_incl_tax = 0
        else :
            match = re.findall(r'\d+\.\d+|\d+', invoice_amount_incl_tax)
            invoice_amount_incl_tax = ""
            for i in range(len(match)):
                invoice_amount_incl_tax += match[i]

        invoice_tax_amount = result_data['Invoice tax amount'].iloc[0]
        if invoice_tax_amount == 'N/A' or invoice_tax_amount == '':
            invoice_tax_amount = 0
        else :
            match = re.findall(r'\d+\.\d+|\d+', invoice_tax_amount)
            invoice_tax_amount = ""
            for i in range(len(match)):
                invoice_tax_amount += match[i]

        # convert amount part to decimal
        new_invoice = Invoice(
            invoice_number = result_data['Invoice number'].iloc[0],
            supplier_name = result_data['Supplier Name'].iloc[0],
            supplier_address_street1 = result_data['Supplier Address Street 1'].iloc[0],
            supplier_address_street2 = result_data['Supplier Address Street 2'].iloc[0],
            supplier_city = result_data['Supplier City'].iloc[0],
            supplier_state = result_data['Supplier State'].iloc[0],
            supplier_zip = result_data['Supplier zip'].iloc[0],
            supplier_country = result_data['Supplier Country'].iloc[0],
            ship_to_street1 = result_data['Ship To Street 1'].iloc[0],
            ship_to_street2 = result_data['Ship To Street 2'].iloc[0],
            ship_to_city = result_data['Ship To City'].iloc[0],
            ship_to_state = result_data['Ship To State'].iloc[0],
            ship_to_zip = result_data['Zip'].iloc[0],
            ship_to_country = result_data['Ship To Country'].iloc[0],
            invoice_currency = result_data['Invoice currency'].iloc[0],
        
            invoice_amount_incl_tax = invoice_amount_incl_tax,
            invoice_tax_amount = invoice_tax_amount,
            purchase_order = result_data['Purchase Order'].iloc[0],
        )
        new_invoice.save()


    # Return the task ID to the client
    return Response({'task_id': task_id})


@api_view(['GET'])
def download_file(request, task_id):
    # file_name = "result.xlsx"
    # # file_name = f"{task_id}_processed.xlsx"
    # file_path = Path(settings.MEDIA_ROOT) / file_name

    # if not os.path.exists(file_path):
    #     return Response({'error': 'File not found or not ready'}, status=404)

    # with open(file_path, 'rb') as fh:
    #     response = HttpResponse(fh.read(), content_type="application/pdf")
    #     response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    #     return response

    # get all rows from the Invoice table and return them as xlsx file
    invoices = Invoice.objects.all()
    df = pd.DataFrame(list(invoices.values()))

    # Create a BytesIO object to store the Excel file
    from io import BytesIO
    excel_file = BytesIO()

    # Write the DataFrame to the BytesIO object as an Excel file
    df.to_excel(excel_file, index=False)

    # Create the HttpResponse object with the Excel file
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="invoices.xlsx"'
    response.write(excel_file.getvalue())
    return response
