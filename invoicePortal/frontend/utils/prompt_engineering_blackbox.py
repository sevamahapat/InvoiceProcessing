'''
@author: 4ashutosh98
'''

import fitz  # PyMuPDF library is called this for some reason
import openai
import pandas as pd
import os
import json
import document_intell as di
from openai import AzureOpenAI
# Set your OpenAI API key here
api_key = 'e203babdbeee456a87a6f8ff29741273'
client = AzureOpenAI(
        azure_endpoint = "https://azure-ai-api-test.openai.azure.com/openai/deployments/GPT4-API-Test/chat/completions?api-version=2024-02-15-preview", 
        api_key=api_key,
        api_version="2024-02-15-preview"
)

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    doc = fitz.open(pdf_path)
    text = ''
    for page in doc:
        text += page.get_text()
    return text

def map_invoices_to_ground_truths(pdf_folder_path, ground_truths_df):
    # Dictionary to hold the mapping of invoice number to text and ground truths
    invoice_map = {}

    for pdf_file in os.listdir(pdf_folder_path):
        if pdf_file.endswith(".pdf"):
            # Extract the invoice number from the file name
            invoice_number = pdf_file.split('.')[0]
            
            # Extract text from the corresponding PDF file
            extracted_text = extract_text_from_pdf(os.path.join(pdf_folder_path, pdf_file))
            
            # Find the corresponding ground truth data for the invoice number
            ground_truth_data = ground_truths_df[ground_truths_df['Invoice number'] == invoice_number]
            
            # If there is a matching ground truth entry, add to the invoice map
            if not ground_truth_data.empty:
                invoice_map[invoice_number] = {
                    'text': extracted_text,
                    'ground_truth': ground_truth_data.iloc[0].to_dict()  # Convert the first matching row to a dictionary
                }

    return invoice_map

def construct_few_shot_prompt(invoice_map, target_invoice_text_path):
    prompt = "Extract the following fields from the invoice text: invoice number, supplier name, supplier address, etc. Provide the extracted data in JSON format.\n\n"
    
    for invoice_number, data in invoice_map.items():
        # Serialize the ground truth dict to a JSON string
        ground_truth_json = json.dumps(data['ground_truth'], default=str)  # default=str to handle any non-serializable types
        
        # Append to the prompt
        prompt += f"Example Invoice Text:\n\"{data['text']}\"\nExtracted Fields:\n{ground_truth_json}\n\n"
        
        # Check if prompt is too long for GPT token limits
        if len(prompt) > 3500:  # Rough check, adjust based on actual token limits
            break  # Stop adding more examples to prevent exceeding token limits

    instructions= """The task is to extract the following 18 fields from the invoice text: 
    Invoice number, Supplier Name, Supplier Address Street 1, Supplier Address Street 2, Supplier City, Supplier State, 
    Supplier zip, Supplier Country, Ship To Street 1, Ship To Street 2, Ship To City, 
    Ship To State, Zip, Ship To Country, Invoice currency, Invoice amount (Incl tax), Invoice tax amount, Purchase Order. 
Just like described in the prompt for other invoices' text and ground truths provided before.
There might be some variations in the invoice text and not all the fiels might be present in all the invoices.
If a field is not present in the invoice, just add "N/A" for that field in the JSON format.
For fields: Invoice amount (Incl tax), Invoice tax amount, the values should be extracted as only number digits in string.
Here is the target invoice JSON text from where you have to extract the aforementioned fields, 
it is formed by lines and table. Note that the table content is extracted for assistance and may not be accurate since the layout varies.
Also the key-value pair could either beformed vertically or horizontally: \n\n"""

    target_invoice_text = di.extract_text_from_pdf(target_invoice_text_path)
    if target_invoice_text is None or target_invoice_text == "":
        return None
    target_invoice_text = json.dumps(target_invoice_text, default=str)

    prompt += instructions + target_invoice_text + "\n\n"

    
    return prompt



def blackbox_gpt_api(prompt):
    """
    Simulates a response from the GPT API without actually calling the service.
    For demonstration purposes, it will return a placeholder string.
    """
    try:
        print("Simulated API call with prompt:")
        print(prompt.encode('utf-8').decode('ascii', 'ignore'))  # Encode to UTF-8 and ignore non-ascii characters
    except Exception as e:
        print(f"Error while printing the prompt: {e}")
    return "This is a simulated response from the GPT API."

def call_gpt_api(prompt):
    """this function uses the GPT API to process the extracted text."""
    # response = openai.Completion.create(
    #     engine="gpt-4",  # or another appropriate engine
    #     prompt=prompt,
    #     temperature=0.7,
    #     max_tokens=300,  # Adjust based on the requirements
    #     top_p=1.0,
    #     frequency_penalty=0.0,
    #     presence_penalty=0.0
    # )
    # return response.choices[0].text.strip()
    if prompt is None or prompt == "":
        return None
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="GPT4-API-Test",  # or another appropriate engine
            temperature=0.7,
            max_tokens=300,  # Adjust based on the requirements
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
    except openai.BadRequestError as e:
        print("Error:", e)
        # Handle gracefully
        return None  # or any other value indicating an error or empty response

    return chat_completion.choices[0].message.content.strip()

def call(target_invoice_text_path):
    # path to the folder containing PDF files used as ground truth for creating the prompts
    pdf_path = 'invoices'
    # target_invoice_text_path = 'target_invoice.pdf'

    # getting all the pdf files from the folder
    file_paths = []

    for pdf_file in os.listdir(pdf_path):
        if pdf_file.endswith(".pdf"):
            file_paths.append(os.path.join(pdf_path, pdf_file))

    invoices_texts = []
    for pdf_file in file_paths:
        # Extract text from PDF
        extracted_text = extract_text_from_pdf(pdf_file)
        invoices_texts.append(extracted_text)


    ground_truths = pd.read_csv('invoices_example\ground_truths.csv')

    # print(ground_truths.head())

    # Map the invoices to their ground truths
    invoice_map = map_invoices_to_ground_truths(pdf_path, ground_truths)

    # Construct the few-shot prompt
    few_shot_prompt = construct_few_shot_prompt(invoice_map, target_invoice_text_path)

    # Now you can call summarize_text_with_chatgpt(few_shot_prompt) as before
    # print(blackbox_gpt_api(few_shot_prompt))
    return call_gpt_api(few_shot_prompt)


