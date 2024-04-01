'''
@Author: sevamahapat
'''
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
import os
import fitz

"""
Remember to remove the key from your code when you're done, and never post it publicly. For production, use
secure methods to store and access your credentials. For more information, see 
https://docs.microsoft.com/en-us/azure/cognitive-services/cognitive-services-security?tabs=command-line%2Ccsharp#environment-variables-and-application-configuration
"""
endpoint = "https://di-accounts-payable-eus2.cognitiveservices.azure.com/"
key = "f87e7b171fa545d09e9c8044037e5252"

# sample document
# formUrl = "https://github.com/0755-11037/Unisy-Invoice-Processing/blob/main/Invoices%20Pool/31061.pdf"
formPath_example = "Unisy-Invoice-Processing/Invoices Pool/31061.pdf"
document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )

def extract_text_from_pdf(formPath, verbose=False):
    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )

    invoice_data = {
        "lines": [],
        "tables": []
    }

    # Open and read the file content
    with open(formPath, "rb") as f:
        document_content = f.read()
        
    poller = document_analysis_client.begin_analyze_document("prebuilt-layout", document_content)
    result = poller.result()

    for idx, style in enumerate(result.styles):
        if verbose:
            print(
                "Document contains {} content".format(
                "handwritten" if style.is_handwritten else "no handwritten"
                )
            )


    for page in result.pages:
        for line_idx, line in enumerate(page.lines):
            if verbose:
                print(
                    "...Line # {} has text content '{}'".format(
                    line_idx,
                    line.content
                    )
                )
            invoice_data["lines"].append(line.content)

        for selection_mark in page.selection_marks:
            if verbose:
                print(
                    "...Selection mark is '{}' and has a confidence of {}".format(
                    selection_mark.state,
                    selection_mark.confidence
                    )
                )

    for table_idx, table in enumerate(result.tables):
        if verbose:
            print(
                "Table # {} has {} rows and {} columns".format(
                table_idx, table.row_count, table.column_count
                )
            )
        header = []
        row = []
        for cell in table.cells:
            if verbose:
                print(
                    "...Cell[{}][{}] has content '{}' with kind {} ".format(
                    cell.row_index,
                    cell.column_index,
                    cell.content,
                    cell.kind
                    )
                )
            if cell.kind == "columnHeader":
                header.append(cell.content)
            if cell.kind == "content":
                row.append(cell.content)
        invoice_data["tables"].append({"header": header, "row": row})

    if verbose:
        print("----------------------------------------")
    return invoice_data

if __name__ == "__main__":
    print(extract_text_from_pdf(formPath_example))
    print("----------------------------------------")
    """Extracts text from a PDF file."""
    doc = fitz.open(formPath_example)
    text = ''
    for page in doc:
        text += page.get_text()
    print(text)
