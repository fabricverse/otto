# import streamlit as st
# import pandas as pd
from openai import OpenAI
import frappe
import json



@frappe.whitelist(allow_guest=True)
def test_method():
    return "Test method called successfully!"

# Set up OpenAI API key

# Function to query OpenAI with a prompt
def query_openai(prompt):
    settings = frappe.get_doc("Otto Settings", "Otto Settings")
    client = OpenAI(api_key=settings.api_key)
    response = client.chat.completions.create(
        model=settings.model,
        messages=[
            {"role": "system", "content": settings.system_prompt_content},
            {"role": "user", "content": prompt},
        ],
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7)
    return response.choices[0].message.content.strip()

@frappe.whitelist()
def prompt():
    

    prompt = "The following is a datase is: WHO IS LETO II"

    # Query OpenAI
    response = query_openai(prompt)

    # Display the response
    # st.write("Auto-completed data:")
    return response

@frappe.whitelist()
def predict_next_customer(company):    
    sales = get_sales(company)
    if len(sales) < 1:
        return
    
    customer_sales_data = get_customer_sales_data(sales)

    prompt = """The following is a dataset of the last {num_of_sales} sales for {company}: ```{customer_sales_data}```
    Predict the next customer for {company}
    """.format(num_of_sales=len(sales), company=company, customer_sales_data=customer_sales_data)
    response = query_openai(prompt)
    result = clean_json(response)
    
    return result



@frappe.whitelist()
def predict_sales_details(customer, company):

    sales = get_sales(company, customer, limit=100)

    if len(sales) < 2:
        return

    invoice_details = get_invoice_details(sales)
    prompt = """
        The following is a dataset of the last {num_of_sales} sales invoices to customer {customer} from the company {company}: 
        ```{invoice_details}```. 
        Predict the next sales invoice details for {customer}
        """.format(num_of_sales=len(sales), company=company, invoice_details=invoice_details, customer=customer)
    
    prediction = query_openai(prompt)
    return prediction

    result = clean_json(prediction)
    frappe.errprint(result)
    return result

def get_invoice_details(invoices):
    invoice_details = []
    
    for inv in invoices:
        invoice_details.append({        
            'due_date': inv.due_date,    
            'currency': inv.currency,
            'selling_price_list': inv.selling_price_list,
            'taxes_and_charges': inv.taxes_and_charges,
            'debit_to': inv.debit_to,
            'terms': inv.terms,
            'items': frappe.get_all('Sales Invoice Item', 
                            filters={'parent': inv.name}, 
                            fields=['item_code', 'item_name', 'description', 'qty', 'uom', 'rate'], limit=0)
        })
    return invoice_details

def clean_json(response_text):

    possible_values = ["```json", "```", "\n"]

    # Replace each possible value in the response text
    for value in possible_values:
        response_text = response_text.replace(value, "")

    try:
        response_json = json.loads(response_text)
        return (response_json)
    except Exception as e:
        print("Failed to decode JSON:", e)
        print("response_text", response_text)
        if response_json:
            print("response_json", response_json)
        return

def get_customer_sales_data(sales):
    customer_sales_data = []
    for sale in sales:
        customer_sales_data.append({
            'customer': sale.customer,
            'invoice_name': sale.name,
            'posting_date': sale.posting_date
        })
    return customer_sales_data

def get_sales(company, customer=None, limit=100):
    customer_query = ""
    if customer:
        customer_query = "AND inv.customer = {customer}".format(customer=frappe.db.escape(customer))
    return frappe.db.sql("""
        SELECT inv.name, inv.customer, inv.due_date, inv.posting_date, inv.terms, inv.currency, inv.selling_price_list, inv.debit_to
        FROM `tabSales Invoice` AS inv        
        WHERE inv.company = {company} AND inv.docstatus = 1
        {customer_query} 
        LIMIT {limit}
    """.format(company=frappe.db.escape(company), limit=limit, customer_query=customer_query), as_dict=1)