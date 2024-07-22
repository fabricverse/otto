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
    customer_sales_data = get_customer_sales_data(sales)

    if len(sales) < 1:
        return

    prompt = """The following is a datase of the last {num_of_sales} sales for {company}: ```{customer_sales_data}```
    Predict the next customer for {company}
    """.format(num_of_sales=len(sales), company=company, customer_sales_data=customer_sales_data)
    response = query_openai(prompt)
    result = clean_json(response)
    
    return result



@frappe.whitelist()
def predict_sales_details(company):    
    """
        On the invoice
            - Tax template
            - Payment due date
            - Fields: debit_to, currency, selling_price_list, terms
        Items
            - Name
            - Description
            - Qty
            - UOM
            - Rate


    """
    return
    sales = get_sales(company)
    customer_sales_data = get_customer_sales_data(sales)

    if len(sales) < 1:
        return

    prompt = """The following is a datase of the last {num_of_sales} sales for {company}: ```{customer_sales_data}```
    Predict the next customer for {company}
    """.format(num_of_sales=len(sales), company=company, customer_sales_data=customer_sales_data)
    response = query_openai(prompt)
    result = clean_json(response)
    
    return result

def clean_json(response_text):

    possible_values = ["```", "json", "\n"]

    # Replace each possible value in the response text
    for value in possible_values:
        response_text = response_text.replace(value, "")

    try:
        print(response_text)
        response_json = json.loads(response_text)
        return (response_json)
    except Exception as e:
        print("Failed to decode JSON:", e)
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

def get_sales(company):
    return frappe.db.sql("""
        SELECT inv.*, items.*
        FROM `tabSales Invoice` inv
            LEFT JOIN `tabSales Invoice Item` items
            ON inv.name = items.parent
        WHERE inv.company = {company} AND inv.docstatus = 1
    """.format(company=frappe.db.escape(company)), as_dict=1)