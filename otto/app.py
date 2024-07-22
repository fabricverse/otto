# import streamlit as st
# import pandas as pd
from openai import OpenAI
import frappe



@frappe.whitelist(allow_guest=True)
def test_method():
	return "Test method called successfully!"

# Set up OpenAI API key

# Function to query OpenAI with a prompt
def query_openai(prompt, settings):

	client = OpenAI(api_key=settings.api_key)
	response = client.chat.completions.create(model="gpt-3.5-turbo",
	messages=[
		{"role": "system", "content": "You are a helpful assistant that autocompletes data entries based on provided information."},
		{"role": "user", "content": prompt},
	],
	max_tokens=150,
	n=1,
	stop=None,
	temperature=0.7)
	return response.choices[0].message.content.strip()

@frappe.whitelist()
def prompt():
	settings = frappe.get_doc("Otto Settings", "Otto Settings")
	#st.title("ERP Auto-Completion Tool")

	# File upload
	# uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

	# if uploaded_file is not None:
		# Load data
		# data = pd.read_csv(uploaded_file)
		# st.write("Data Preview:")
		# st.write(data.head())

		# # User selects target variable
		# target_variable = st.selectbox("Select the target variable (e.g., customer name):", data.columns)

		# # User inputs value for target variable
		# target_value = st.text_input(f"Enter value for {target_variable}:")

		# if target_value:
			# Prepare the prompt
			#prompt = f"The following is a dataset:\n{data.to_csv(index=False)}\n\nComplete the missing values for the row where {target_variable} is '{target_value}':"

	prompt = f"The following is a datase is: WHO IS LETO II"

	# Query OpenAI
	response = query_openai(prompt, settings)

	# Display the response
	# st.write("Auto-completed data:")
	return response
